import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property string title: "暂无项目"
    property string description: "请先创建一个同步项目。"

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(parent.width - 64, 520)
        spacing: 14

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 72
            height: 72
            radius: 24
            color: "#eef4ff"
            border.color: "#dbeafe"

            Text {
                anchors.centerIn: parent
                text: "↗"
                color: "#2563eb"
                font.pixelSize: 34
                font.weight: Font.Bold
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.title
            color: "#111827"
            font.pixelSize: 25
            font.weight: Font.Bold
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            Layout.fillWidth: true
            text: root.description
            color: "#64748b"
            font.pixelSize: 14
            lineHeight: 1.25
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }
}
