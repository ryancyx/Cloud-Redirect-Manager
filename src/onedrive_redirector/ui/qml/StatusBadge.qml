import QtQuick 2.15

Rectangle {
    id: root

    property string statusText: "未知状态"
    property string statusIcon: "○"
    property color statusColor: "#64748b"

    radius: 999
    implicitHeight: 30
    implicitWidth: Math.max(112, row.implicitWidth + 22)
    color: Qt.rgba(statusColor.r, statusColor.g, statusColor.b, 0.11)
    border.width: 1
    border.color: Qt.rgba(statusColor.r, statusColor.g, statusColor.b, 0.20)

    Row {
        id: row
        anchors.centerIn: parent
        spacing: 7

        Text {
            text: root.statusIcon || "○"
            color: root.statusColor
            font.pixelSize: 13
            font.weight: Font.Bold
            verticalAlignment: Text.AlignVCenter
        }

        Text {
            text: root.statusText || "未知状态"
            color: root.statusColor
            font.pixelSize: 13
            font.weight: Font.DemiBold
            verticalAlignment: Text.AlignVCenter
        }
    }
}
