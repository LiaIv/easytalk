//
//  ContentView.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 28.03.2025.
// 

import SwiftUI

// Структура для выбора уровня английского
struct EnglishLevelSelectionView: View {
    @Binding var email: String
    @Binding var isShowingEnglishLevel: Bool
    @State private var selectedLevel: EnglishLevel? = nil
    
    enum EnglishLevel: String, CaseIterable {
        case beginner = "Начинающий"
        case intermediate = "Средний"
        case advanced = "Продвинутый"
        
        var emoji: String {
            switch self {
            case .beginner: return "🐤" // Цыпленок
            case .intermediate: return "🎓" // Шапка выпускника
            case .advanced: return "🦉" // Сова
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 30) {
            Text("Какой у вас уровень английского?")
                .font(.system(size: 28, weight: .bold))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 20)
                .padding(.top, 50)
            
            ForEach(EnglishLevel.allCases, id: \.self) { level in
                Button {
                    selectedLevel = level
                } label: {
                    HStack {
                        Text(level.emoji)
                            .font(.system(size: 24))
                            .padding(.trailing, 10)
                        
                        Text(level.rawValue)
                            .font(.system(size: 20, weight: .medium))
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(selectedLevel == level ? Color("orange") : Color.clear, lineWidth: 2)
                    )
                }
                .buttonStyle(PlainButtonStyle())
                .padding(.horizontal, 20)
            }
            
            Spacer()
            
            Button {
                if selectedLevel != nil {
                    // Здесь можно сохранить уровень в UserDefaults
                    UserDefaults.standard.set(selectedLevel?.rawValue, forKey: "englishLevel")
                    
                    // Закрываем этот экран и переходим к основному интерфейсу
                    isShowingEnglishLevel = false
                }
            } label: {
                Text("Далее")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(
                        selectedLevel != nil ?
                        LinearGradient(colors: [Color("yellow"), Color("orange")], startPoint: .leading, endPoint: .trailing) :
                        LinearGradient(colors: [Color.gray.opacity(0.5), Color.gray.opacity(0.7)], startPoint: .leading, endPoint: .trailing)
                    )
                    .cornerRadius(12)
                    .padding(.horizontal, 20)
                    .padding(.bottom, 30)
                    .font(.title3.bold())
                    .foregroundStyle(.black)
            }
            .disabled(selectedLevel == nil)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color("lightBlue").edgesIgnoringSafeArea(.all))
    }
}

struct AuthView: View {
    @State private var isAuth = true
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var isTabViewShow = false
    @State private var isShowAlert = false
    @State private var alertMessage = ""
    @State private var showEnglishLevelView = false


    var body: some View {
        VStack(spacing: 20) {
            Text(isAuth ? "Авторизация" : "Регистрация")
                .padding(isAuth ? 16 : 24)
                .padding(.horizontal,30)
                .font(.title2.bold())
                .background(Color("whiteAlpha"))
                .cornerRadius(isAuth ? 30 : 60)
            VStack{
                TextField("Введите email", text: $email)
                    .padding()
                    .background(Color("whiteAlpha"))
                    .cornerRadius(12)
                    .padding(8)
                    .padding(.horizontal, 12)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                SecureField("Введите пароль", text: $password)
                    .padding()
                    .background(Color("whiteAlpha"))
                    .cornerRadius(12)
                    .padding(8)
                    .padding(.horizontal, 12)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                
                if !isAuth {
                    SecureField("Повторите пароль", text: $confirmPassword)
                        .padding()
                        .background(Color("whiteAlpha"))
                        .cornerRadius(12)
                        .padding(8)
                        .padding(.horizontal, 12)
                        .autocapitalization(.none)
                        .disableAutocorrection(true)
                }
                
                Button {
                    if isAuth {
                        print("Авторизация пользователя через firebase")
                        
                        AuthService.shared.signIn(email: self.email, password: self.password) { result in
                            switch result {
                            case .success(_):
                                // Set user as logged in
                                UserDefaults.setLoggedIn(value: true)
                                isTabViewShow.toggle()
                            case .failure(let error):
                                alertMessage = "Ошибка авторизации: \(error.localizedDescription)"
                                isShowAlert.toggle()
                            }
                        }
                        
                    } else {
                        print("Регистрация пользователя")
                        
                        guard password == confirmPassword else {
                            self.alertMessage = "Пароли не совпадают"
                            self.isShowAlert.toggle()
                            return
                        }
                        
                        
                        AuthService.shared.signUp(email: self.email, password: self.password) { result in
                            switch result {
                                
                            case .success(let user):
                                print("Успешная регистрация пользователя: \(user.email ?? "")")
                                // Set user as logged in
                                UserDefaults.setLoggedIn(value: true)
                                // Вместо показа алерта, показываем экран выбора уровня английского
                                self.showEnglishLevelView = true
                                // Оставим эти строки для сохранения состояния
                                self.password = ""
                                self.confirmPassword = ""
                            case .failure(let error):
                                alertMessage = "Ошибка регистрации \(error.localizedDescription)"
                                self.isShowAlert.toggle()
                            }
                        }
                    }
                } label: {
                    Text(isAuth ? "Войти" : "Создать аккаунт")
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(LinearGradient(colors: [Color("yellow"),Color("orange")], startPoint: .leading, endPoint: .trailing))
                        .cornerRadius(12)
                        .padding(8)
                        .padding(.horizontal, 12)
                        .font(.title3.bold())
                        .foregroundStyle(.black)
                }
                Button {
                    isAuth.toggle()
                } label: {
                    Text(isAuth ? "Еще не с нами?" : "Уже есть аккаунт!")
                        .padding(.horizontal)
                        .frame(maxWidth: .infinity)
                        .cornerRadius(12)
                        .padding(8)
                        .padding(.horizontal, 12)
                        .font(.title3.bold())
                        .foregroundStyle(Color("darkBrown"))
                }

            }
            .padding()
            .padding(.top, 16)
            .background(Color("whiteAlpha"))
            .cornerRadius(20)
            .padding(isAuth ? 30 : 12)
            .alert(alertMessage, isPresented: $isShowAlert) {
                Button {} label: {
                    Text("OK")
                }

            }

            
        }.frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Image("bg")
                .ignoresSafeArea()
                .blur(radius: isAuth ? 0 : 9))
            .animation(Animation.easeInOut(duration: 0.3), value: isAuth)
            .fullScreenCover(isPresented: $isTabViewShow) {
                
                let mainTabBarViewModel = MainTabBarViewModel(user: AuthService.shared.currentUser!)
                MainTabBar(viewModel: mainTabBarViewModel)
            }
            .fullScreenCover(isPresented: $showEnglishLevelView) {
                EnglishLevelSelectionView(email: $email, isShowingEnglishLevel: $showEnglishLevelView)
            }
            .onChange(of: showEnglishLevelView) { _, newValue in
                // Когда экран выбора уровня закрывается, проверяем уровень и переходим к основному экрану
                if !newValue && UserDefaults.standard.string(forKey: "englishLevel") != nil {
                    // Set user as logged in when they finish the level selection after registration
                    UserDefaults.setLoggedIn(value: true)
                    isTabViewShow = true
                }
            }
    }
}

#Preview {
    AuthView()
}
