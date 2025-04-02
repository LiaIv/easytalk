//
//  EasyTalkProjectApp.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 28.03.2025.
//

import SwiftUI
import Firebase

@main
struct EasyTalkProjectApp: App {
    
    @UIApplicationDelegateAdaptor private var appDelegate: AppDelegate
    
    var body: some Scene {
        WindowGroup {
            AuthView()
        }
    }
    
    class AppDelegate: NSObject, UIApplicationDelegate {
        
        func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
            
            FirebaseApp.configure()
            print("App Delegete")
            
            return true
        }
    }
}
