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
                
                Spacer().frame(height: 30)

                Text("выбери свой уровень")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity, alignment: .center)

                HStack(spacing: 20) {
                    ForEach(levels, id: \.self) { level in
                        VStack {
                            Image(stars[level] ?? "white_star")
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(width: 40, height: 40)

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
                .padding(.top, 20)
                .frame(maxWidth: .infinity, alignment: .center) // Выравниваем весь HStack по центру
                
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
            .background(
                Image("backgroundImage")
                    .resizable()
                    .ignoresSafeArea()
            )
            .onAppear {
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
                            userName = newUserName
                            showEditBanner = false
                            UserDefaults.standard.set(userName, forKey: userNameKey)
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

    // Обновляем состояние звезд
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



