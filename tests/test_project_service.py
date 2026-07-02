from pathlib import Path

import pytest

import onedrive_redirector.core.project_service as project_service_module
from onedrive_redirector.core.models import Project
from onedrive_redirector.core.project_service import ProjectService
from onedrive_redirector.core.project_store import ProjectStore
from onedrive_redirector.core.settings_store import SettingsStore


def make_service(tmp_path: Path) -> tuple[ProjectService, Path]:
    settings_store = SettingsStore(tmp_path / "appdata")
    root = tmp_path / "OneDriveRedirector"
    service = ProjectService(settings_store)
    service.save_onedrive_root(str(root))
    return service, root


def add_project(
    root: Path,
    *,
    project_id: str = "conflict-test",
    local_path: str | None = None,
    cloud_relative_path: str = "data/cloud-conflict",
) -> Project:
    store = ProjectStore(root)
    project = Project(
        id=project_id,
        name="Conflict Test",
        local_path=local_path or str(root.parent / "ODR_LocalTest" / "LocalConflict"),
        cloud_relative_path=cloud_relative_path,
        created_at="2026-07-02T10:00:00+08:00",
        updated_at="2026-07-02T10:00:00+08:00",
    )
    store.add_project(project)
    return project


def test_delete_project_without_delete_cloud_or_local_link_removes_config_only(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "LocalConflict"
    local_link.mkdir()
    add_project(root, local_path=str(local_link))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)
    (cloud_target / "cloud.txt").write_text("cloud", encoding="utf-8")

    service.delete_project("conflict-test", False, False)

    assert ProjectStore(root).load().get_project("conflict-test") is None
    assert cloud_target.exists()
    assert local_link.exists()


def test_delete_project_with_delete_cloud_and_local_link_removes_both(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "LocalConflict"
    local_link.mkdir()
    add_project(root, local_path=str(local_link))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)
    (cloud_target / "cloud.txt").write_text("cloud", encoding="utf-8")
    other_project_dir = root / "data" / "other-project"
    other_project_dir.mkdir(parents=True)
    (other_project_dir / "keep.txt").write_text("keep", encoding="utf-8")
    backup_dir = local_parent / "LocalConflict_backup"
    backup_dir.mkdir()

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: True)

    def fake_remove_junction(path: Path) -> None:
        Path(path).rmdir()

    monkeypatch.setattr(project_service_module, "remove_junction", fake_remove_junction)

    service.delete_project("conflict-test", True, True)

    assert ProjectStore(root).load().get_project("conflict-test") is None
    assert not cloud_target.exists()
    assert not local_link.exists()
    assert local_parent.exists()
    assert backup_dir.exists()
    assert other_project_dir.exists()


def test_delete_project_with_delete_both_deletes_local_link_before_cloud(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "DeleteBothTest"
    local_link.mkdir()
    add_project(
        root,
        project_id="delete-both-test",
        local_path=str(local_link),
        cloud_relative_path="data/delete-both-test",
    )
    cloud_target = root / "data" / "delete-both-test"
    cloud_target.mkdir(parents=True)
    (cloud_target / "cloud.txt").write_text("cloud", encoding="utf-8")

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: True)
    events: list[str] = []

    def fake_remove_junction(path: Path) -> None:
        events.append("remove_junction")
        Path(path).rmdir()

    def fake_remove_tree(path: Path) -> None:
        events.append("remove_tree")
        import shutil
        shutil.rmtree(path)

    monkeypatch.setattr(project_service_module, "remove_junction", fake_remove_junction)
    monkeypatch.setattr(project_service_module, "remove_tree", fake_remove_tree)

    service.delete_project("delete-both-test", True, True)

    assert events == ["remove_junction", "remove_tree"]
    assert ProjectStore(root).load().get_project("delete-both-test") is None
    assert not local_link.exists()
    assert not cloud_target.exists()
    assert local_parent.exists()


def test_delete_project_with_delete_local_link_only_removes_link_and_keeps_cloud(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "LocalConflict"
    local_link.mkdir()
    add_project(root, local_path=str(local_link))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: True)

    def fake_remove_junction(path: Path) -> None:
        Path(path).rmdir()

    monkeypatch.setattr(project_service_module, "remove_junction", fake_remove_junction)

    service.delete_project("conflict-test", False, True)

    assert ProjectStore(root).load().get_project("conflict-test") is None
    assert not local_link.exists()
    assert local_parent.exists()
    assert cloud_target.exists()


def test_delete_local_link_rejects_ordinary_directory_and_preserves_contents(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_dir = tmp_path / "ODR_LocalTest" / "LocalConflict"
    local_dir.mkdir(parents=True)
    (local_dir / "local.txt").write_text("keep", encoding="utf-8")
    add_project(root, local_path=str(local_dir))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    with pytest.raises(RuntimeError, match="本地路径不是链接"):
        service.delete_project("conflict-test", False, True)

    assert ProjectStore(root).load().get_project("conflict-test") is not None
    assert local_dir.exists()
    assert (local_dir / "local.txt").exists()
    assert cloud_target.exists()


def test_delete_cloud_rejects_onedrive_root(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    with pytest.raises(Exception):
        service._get_safe_cloud_delete_path(root, "")


def test_delete_cloud_rejects_data_root(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    with pytest.raises(Exception):
        service._get_safe_cloud_delete_path(root, "data")


def test_delete_cloud_rejects_parent_escape(tmp_path: Path) -> None:
    service, root = make_service(tmp_path)
    with pytest.raises(Exception):
        service._get_safe_cloud_delete_path(root, "data/../../escape")


def test_delete_project_includes_underlying_cloud_delete_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    local_parent = tmp_path / "ODR_LocalTest"
    local_parent.mkdir()
    local_link = local_parent / "LocalConflict"
    local_link.mkdir()
    add_project(root, local_path=str(local_link))
    cloud_target = root / "data" / "cloud-conflict"
    cloud_target.mkdir(parents=True)

    def fake_remove_tree(path: Path) -> None:
        raise RuntimeError("rmdir fallback still failed")

    monkeypatch.setattr(project_service_module, "remove_tree", fake_remove_tree)

    with pytest.raises(RuntimeError, match="删除 OneDrive 目标文件夹失败：") as exc_info:
        service.delete_project("conflict-test", True, False)

    message = str(exc_info.value)
    assert f"路径：{cloud_target}" in message
    assert "原因：rmdir fallback still failed" in message
    assert ProjectStore(root).load().get_project("conflict-test") is not None


def make_project_data(
    tmp_path: Path,
    *,
    project_id: str = "sync-test",
    local_name: str = "LocalSync",
    cloud_relative_path: str = "data/sync-test",
) -> dict[str, str]:
    return {
        "id": project_id,
        "name": "Sync Test",
        "local_path": str(tmp_path / "ODR_LocalTest" / local_name),
        "cloud_relative_path": cloud_relative_path,
    }


def test_create_project_with_local_empty_and_cloud_empty_creates_junction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    data = make_project_data(tmp_path, local_name="LocalEmpty", cloud_relative_path="data/cloud-empty")
    local_path = Path(data["local_path"])
    local_path.mkdir(parents=True)
    cloud_path = root / "data" / "cloud-empty"
    cloud_path.mkdir(parents=True)
    events: list[tuple[Path, Path]] = []

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    def fake_create_junction(link_path: Path, target_path: Path) -> None:
        link = Path(link_path)
        target = Path(target_path)
        assert not link.exists()
        assert target.exists()
        events.append((link, target))
        link.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "create_junction", fake_create_junction)

    service.create_project(data)

    assert events == [(local_path, cloud_path)]
    assert ProjectStore(root).load().get_project("sync-test") is not None
    assert cloud_path.exists()
    assert local_path.exists()


def test_create_project_with_local_empty_and_cloud_missing_creates_cloud_and_junction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    data = make_project_data(tmp_path, local_name="LocalEmptyMissing", cloud_relative_path="data/cloud-missing")
    local_path = Path(data["local_path"])
    local_path.mkdir(parents=True)
    cloud_path = root / "data" / "cloud-missing"
    events: list[tuple[Path, Path]] = []

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    def fake_create_junction(link_path: Path, target_path: Path) -> None:
        link = Path(link_path)
        target = Path(target_path)
        assert not link.exists()
        assert target.exists()
        events.append((link, target))
        link.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "create_junction", fake_create_junction)

    service.create_project(data)

    assert events == [(local_path, cloud_path)]
    assert cloud_path.exists()
    assert ProjectStore(root).load().get_project("sync-test") is not None


def test_create_project_with_local_missing_and_cloud_empty_creates_junction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    data = make_project_data(tmp_path, local_name="LocalMissing", cloud_relative_path="data/cloud-empty-existing")
    local_path = Path(data["local_path"])
    cloud_path = root / "data" / "cloud-empty-existing"
    cloud_path.mkdir(parents=True)
    events: list[tuple[Path, Path]] = []

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    def fake_create_junction(link_path: Path, target_path: Path) -> None:
        link = Path(link_path)
        target = Path(target_path)
        assert not link.exists()
        assert target.exists()
        events.append((link, target))
        link.parent.mkdir(parents=True, exist_ok=True)
        link.mkdir()

    monkeypatch.setattr(project_service_module, "create_junction", fake_create_junction)

    service.create_project(data)

    assert events == [(local_path, cloud_path)]
    assert ProjectStore(root).load().get_project("sync-test") is not None
    assert cloud_path.exists()
    assert local_path.exists()


def test_create_project_with_local_empty_and_cloud_non_empty_creates_junction_and_keeps_cloud_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    data = make_project_data(tmp_path, local_name="LocalEmptyCloudData", cloud_relative_path="data/cloud-has-data")
    local_path = Path(data["local_path"])
    local_path.mkdir(parents=True)
    cloud_path = root / "data" / "cloud-has-data"
    cloud_path.mkdir(parents=True)
    cloud_file = cloud_path / "cloud.txt"
    cloud_file.write_text("cloud", encoding="utf-8")

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    def fake_create_junction(link_path: Path, target_path: Path) -> None:
        link = Path(link_path)
        target = Path(target_path)
        assert not link.exists()
        assert target == cloud_path
        link.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "create_junction", fake_create_junction)

    service.create_project(data)

    assert cloud_file.read_text(encoding="utf-8") == "cloud"
    assert ProjectStore(root).load().get_project("sync-test") is not None
    assert local_path.exists()


def test_create_project_with_local_non_empty_and_cloud_non_empty_still_conflicts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    data = make_project_data(tmp_path, local_name="LocalConflictCreate", cloud_relative_path="data/cloud-conflict-create")
    local_path = Path(data["local_path"])
    local_path.mkdir(parents=True)
    (local_path / "local.txt").write_text("local", encoding="utf-8")
    cloud_path = root / "data" / "cloud-conflict-create"
    cloud_path.mkdir(parents=True)
    (cloud_path / "cloud.txt").write_text("cloud", encoding="utf-8")

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    with pytest.raises(RuntimeError, match="CONFLICT"):
        service.create_project(data)

    assert ProjectStore(root).load().get_project("sync-test") is None


def test_create_project_with_wrong_or_broken_junction_still_rejects(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    service, root = make_service(tmp_path)
    data = make_project_data(tmp_path, local_name="BrokenJunction", cloud_relative_path="data/broken-junction")

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: Path(path) == Path(data["local_path"]))
    monkeypatch.setattr(project_service_module, "points_to_target", lambda link, target: False)

    with pytest.raises(RuntimeError, match="本地路径已经是链接，但未指向当前 OneDrive 目标文件夹。"):
        service.create_project(data)

    assert ProjectStore(root).load().get_project("sync-test") is None


def test_create_project_restores_empty_local_directory_when_junction_creation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, root = make_service(tmp_path)
    data = make_project_data(tmp_path, local_name="LocalRestoreOnFailure", cloud_relative_path="data/restore-on-failure")
    local_path = Path(data["local_path"])
    local_path.mkdir(parents=True)
    cloud_path = root / "data" / "restore-on-failure"
    cloud_path.mkdir(parents=True)

    monkeypatch.setattr(project_service_module, "is_junction_or_reparse_point", lambda path: False)

    def fake_create_junction(link_path: Path, target_path: Path) -> None:
        assert not Path(link_path).exists()
        raise RuntimeError("junction creation failed")

    monkeypatch.setattr(project_service_module, "create_junction", fake_create_junction)

    with pytest.raises(RuntimeError, match="junction creation failed"):
        service.create_project(data)

    assert local_path.exists()
    assert local_path.is_dir()
    assert list(local_path.iterdir()) == []
    assert cloud_path.exists()
    assert ProjectStore(root).load().get_project("sync-test") is None