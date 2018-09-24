import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.11
import QtWebEngine 1.7

ApplicationWindow {
    id: window
    visible: true

    TabView {
        id: tabs
        objectName: "tabs"
        width: 1280
        height: 768
    }
}
