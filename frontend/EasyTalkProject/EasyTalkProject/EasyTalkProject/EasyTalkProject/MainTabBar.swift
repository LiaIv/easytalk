//
//  MainTabBar.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI

struct MainTabBar: View {
    
    var viewModel: MainTabBarViewModel
    
    var body: some View {
        TabView {
            EducationView()
                .tabItem {
                    VStack {
                        Image(systemName: "book")
                        Text("учебник")
                    }
                }
            
            GameView()
                .tabItem {
                    VStack {
                        Image(systemName: "gamecontroller.circle")
                        Text("мини-игры")
                    }
                }
            
            ProfileView()
                .tabItem {
                    VStack {
                        Image(systemName: "person")
                        Text("профиль")
                    }
                }
        }
    }
}

