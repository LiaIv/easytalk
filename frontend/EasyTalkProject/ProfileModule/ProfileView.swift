//
//  ProfileView.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI
import PhotosUI

struct ProfileView: View {
    @State private var userName: String = "Ваше имя"
    @State private var newUserName: String = ""
    @State private var showEditBanner: Bool = false
    @FocusState private var isTextFieldFocused: Bool

    @State private var selectedPhoto: PhotosPickerItem? = nil
    @State private var avatarImage: Image = Image("avatar")
    
    @State private var levels = ["Begin", "Pre-Inter", "Interm", "Soon!"]
    @State private var selectedLevel = "Begin"
    @State private var stars = [
        "Begin": "gold_star",
        "Pre-Inter": "white_star",
        "Interm": "white_star",
        "Soon!": "white_star"
    ]

    @State private var showExitAppConfirmation = false
    @StateObject private var vm = ProfileViewModel()
    @State private var achievementsNotAvailable: Bool = true // когда достижения будут реализованы
    @State private var showingLoginView = false
    
    let userNameKey = "userNameKey"
    let userImageKey = "userImageKey"
    let userLevelKey = "userLevelKey"

    var body: some View {
        ZStack {
            VStack {
                Spacer().frame(height: 10)
                HStack(alignment: .center, spacing: 25) {
                    PhotosPicker(selection: $selectedPhoto, matching: .images, photoLibrary: .shared()) {
                        avatarImage
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(width: 80, height: 80)
                            .clipShape(Circle())
                            .shadow(radius: 4)
                    }

                    VStack(alignment: .leading, spacing: 8) {
                        Button(action: {
                            newUserName = userName
                            showEditBanner = true
                        }) {
                            Text(userName)
                                .font(.headline)
                                .foregroundColor(.black)
                                .frame(width: 225, height: 30, alignment: .leading)
                                .padding(.leading, 5)
                                .background(
                                    RoundedRectangle(cornerRadius: 7)
                                        .fill(Color.white.opacity(0.38))
                                )
                        }

                        Text("ID 18767584")
                            .font(.subheadline)
                            .foregroundColor(.black)
                            .padding(.leading, 5)
                    }

                    Spacer()
                }
                .padding(.horizontal)
                .padding(.top, 20)
                
                Spacer().frame(height: 40)

                Text("выбери свой уровень")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity, alignment: .center)

                HStack(spacing: 30) {
                    ForEach(levels, id: \.self) { level in
                        VStack {
                            Image(stars[level] ?? "white_star")
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(width: 40, height: 40)
                                .scaleEffect(level == selectedLevel ? 1.2 : 1.0)
                                .animation(.easeInOut(duration: 0.3), value: selectedLevel)

                            Text(level)
                                .foregroundColor(.black)
                                .padding(.top, 10)
                                .font(.subheadline)
                        }
                        .frame(maxWidth: .infinity, alignment: .center)
                        .onTapGesture {
                            if level != "Soon!" {
                                self.selectedLevel = level
                                self.updateStars(for: level)
                                UserDefaults.standard.set(level, forKey: userLevelKey)
                            }
                        }
                    }
                }

                // Stats chart
                ProgressStatsView()
                    .padding(.top, 20)

                VStack {
                    Text("Твои достижения")
                        .font(.headline)
                        .foregroundColor(.black)
                        .padding(.top, 10)

                    if achievementsNotAvailable {
                        Text("Soon!")
                            .font(.subheadline)
                            .foregroundColor(.black)
                            .frame(width: 300, height: 60)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(Color.white.opacity(0.7))
                            )
                            .frame(maxWidth: .infinity)
                            .padding(.top, 10)
                    } else {
                        // Здесь будет код для отображения достижений, когда они будут реализованы
                    }
                }

                .padding(.top, 5)
                .frame(maxWidth: .infinity, alignment: .center)
                
                VStack {
                    Spacer()
                    Button(action: {
                        showExitAppConfirmation = true
                    }) {
                        Text("Выйти")
                            .font(.system(size: 16, weight: .bold))
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.red.opacity(0.8))
                            .cornerRadius(12)
                            .padding(.horizontal, 30)
                            .padding(.bottom, 60)
                    }
                }
                .alert("Выйти из приложения?", isPresented: $showExitAppConfirmation) {
                    Button("Отмена", role: .cancel) {}
                    Button("Да, выйти", role: .destructive) {
                        // Очищаем данные сессии
                        UserDefaults.standard.removeObject(forKey: userNameKey)
                        UserDefaults.standard.removeObject(forKey: userImageKey)
                        UserDefaults.standard.removeObject(forKey: userLevelKey)
                        UserDefaults.standard.removeObject(forKey: "englishLevel")
                        
                        // Сбрасываем статус авторизации
                        UserDefaults.setLoggedIn(value: false)
                        
                        // Переход на экран авторизации
                        showingLoginView = true
                    }
                }
                
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
            .background(
                Image("backgroundProfile")
                    .resizable()
                    .ignoresSafeArea()
            )
            .fullScreenCover(isPresented: $showingLoginView) {
                AuthView()
            }
            .onAppear {
                vm.load()
                // Загрузка имени
                if let savedName = UserDefaults.standard.string(forKey: userNameKey) {
                    userName = savedName
                }

                // Загрузка фото
                if let imageData = UserDefaults.standard.data(forKey: userImageKey),
                   let uiImage = UIImage(data: imageData) {
                    avatarImage = Image(uiImage: uiImage)
                }

                // Загрузка выбранного уровня
                if let savedLevel = UserDefaults.standard.string(forKey: userLevelKey) {
                    selectedLevel = savedLevel
                    updateStars(for: savedLevel)
                }
            }
            .onChange(of: selectedPhoto) {
                Task {
                    if let data = try? await
                        selectedPhoto?.loadTransferable(type: Data.self),
                       let uiImage = UIImage(data: data) {
                        avatarImage = Image(uiImage: uiImage)
                        UserDefaults.standard.set(data, forKey: userImageKey)
                    }
                }
            }
            .onChange(of: vm.profile) { newProfile in
                if let profile = newProfile {
                    self.userName = profile.displayName ?? profile.email
                    // при необходимости можно обновить selectedLevel
                }
            }
            // функция изменения имени
            if showEditBanner {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()

                VStack(spacing: 20) {
                    Text("Как вас зовут?")
                        .font(.title2)
                        .foregroundColor(.black)

                    TextField("Введите новое имя", text: $newUserName)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(10)
                        .padding(.horizontal, 20)
                        .focused($isTextFieldFocused)

                    HStack(spacing: 30) {
                        Button(action: {
                            showEditBanner = false
                        }) {
                            Text("назад")
                                .font(.system(size: 14))
                                .foregroundColor(.white)
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(Color.gray)
                                .cornerRadius(10)
                        }

                        Button(action: {
                            let trimmedName = newUserName.trimmingCharacters(in: .whitespacesAndNewlines)
                            
                            if !trimmedName.isEmpty && trimmedName.count <= 22 {
                                userName = trimmedName
                                vm.updateDisplayName(trimmedName)
                                showEditBanner = false
                                UserDefaults.standard.set(userName, forKey: userNameKey)
                            }
                        }) {
                            Text("изменить")
                                .font(.system(size: 14))
                                .foregroundColor(.white)
                                .padding()
                                .frame(maxWidth: .infinity)
                                .background(Color.blue)
                                .cornerRadius(10)
                        }
                    }
                    .padding(.horizontal, 20)
                }
                .padding()
                .frame(width: 300)
                .background(Color.white)
                .cornerRadius(20)
                .shadow(radius: 10)
                .onAppear {
                    isTextFieldFocused = true
                }
            }
        }
    }

    func updateStars(for level: String) {
        for (key, _) in stars {
            if key == level {
                stars[key] = "gold_star"
            } else {
                stars[key] = "white_star"
            }
        }
    }
}

#Preview {
    ProfileView()
}



