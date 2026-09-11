import QtQuick
import QtQuick.Controls

// A themed primary/secondary action button. Doesn't rely on Material's
// default filled-button chrome for `highlighted: true` -- that chrome
// depends on an elevation/shadow effect that renders as a fully
// invisible (no fill, no border) button under this app's offscreen
// test harness, confirmed via isolated reproduction outside any of
// this app's own QML. Painting the fill explicitly sidesteps that
// entirely and keeps every "Confirm X" button on-brand (gold pill)
// instead of Material's generic blue/teal.
Button {
    id: control
    property bool primary: true

    contentItem: Text {
        text: control.text
        font.pixelSize: Theme.fsBody
        font.bold: true
        color: control.primary ? Theme.bg : Theme.text
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        implicitHeight: 48
        // Same corner radius as MToggleButton's Active/Inactive button --
        // a blockier, less pill-like rounded-rect reads more consistent
        // across the app than the two shapes sitting side by side with
        // slightly different roundedness (e.g. a Resources row's Use/
        // Restore buttons next to an Active toggle).
        radius: 8
        color: control.primary
            ? (control.pressed ? Qt.darker(Theme.gold, 1.15) : Theme.gold)
            : (control.pressed ? Theme.surf3 : Theme.surf2)
        border.color: control.primary ? "transparent" : Theme.border
        border.width: control.primary ? 0 : 1
        opacity: control.enabled ? 1.0 : 0.5
    }
}
