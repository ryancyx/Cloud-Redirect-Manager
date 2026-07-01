import QtQuick 2.15

Item {
    id: control

    property string text: ""
    property color baseColor: "#2563eb"
    property color hoverColor: subtle ? "#eef3f9" : "#dbeafe"
    property color pressedColor: subtle ? "#e2e8f0" : "#bfdbfe"
    property color textColor: subtle ? "#334155" : "#ffffff"
    property color disabledColor: "#eef2f7"
    property bool subtle: false

    signal clicked()

    implicitHeight: 40
    implicitWidth: Math.max(96, label.implicitWidth + 34)
    opacity: enabled ? 1.0 : 0.68

    Rectangle {
        anchors.fill: parent
        radius: 12
        color: !control.enabled ? control.disabledColor
             : mouseArea.pressed ? control.pressedColor
             : mouseArea.containsMouse ? control.hoverColor
             : control.subtle ? "#f8fafc" : control.baseColor
        border.width: control.subtle || mouseArea.containsMouse ? 1 : 0
        border.color: !control.enabled ? "#e5e7eb"
             : mouseArea.pressed ? "#93c5fd"
             : mouseArea.containsMouse ? "#bfdbfe"
             : control.subtle ? "#d7dfe9" : "transparent"
    }

    Text {
        id: label
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        text: control.text
        color: !control.enabled ? "#94a3b8"
             : mouseArea.containsMouse || mouseArea.pressed ? (control.subtle ? "#0f172a" : "#1d4ed8")
             : control.subtle ? "#334155" : control.textColor
        font.pixelSize: 14
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: control.enabled
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: control.clicked()
    }
}
