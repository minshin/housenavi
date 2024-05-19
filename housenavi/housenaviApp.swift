//
//  housenaviApp.swift
//  housenavi
//
//  Created by hiroshi on 2024/05/04.
//

import SwiftUI
import FirebaseCore
import FirebaseAuth

//如果您使用的是 SwiftUI，则必须创建应用委托并通过 UIApplicationDelegateAdaptor 或 NSApplicationDelegateAdaptor 将其附加到 App 结构体。您还必须停用应用委托调配。如需了解详情，请参阅 SwiftUI 说明。

class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
        print("Use Firebase library to configure APIs")
        FirebaseApp.configure()
        return true
    }
}

@main
struct housenaviApp: App {
    // register app delegate for Firebase setup
    @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    var body: some Scene {
        WindowGroup {
            NavigationView {
                ContentView()
            }
        }
    }
}
