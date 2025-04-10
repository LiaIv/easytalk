//
//  MainTabBarViewModel.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import Foundation
import FirebaseAuth

class MainTabBarViewModel: ObservableObject {
    @Published var user: User
    
    init(user: User) {
        self.user = user
    }
}
