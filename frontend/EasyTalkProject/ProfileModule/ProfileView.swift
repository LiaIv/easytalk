//
//  ProfileView.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI

struct ProfileView: View {
    @State private var userName: String = "Ваше имя"
    @State private var newUserName: String = ""
    @State private var showEditBanner: Bool = false
    @FocusState private var isTextFieldFocused: Bool

    var body: some View {
        ZStack {
            VStack {
                HStack(alignment: .center, spacing: 25) {
                    Image("avatar")
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 80, height: 80)
                        .clipShape(Circle())
                        .shadow(radius: 4)

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

                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
            .background(
                Image("backgroundImage")
                    .resizable()
                    .ignoresSafeArea()
            )

            
            if showEditBanner {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()

                VStack(spacing: 20) {
                    Text("Как вас зовут?")
                        .font(.title2)
                        .foregroundColor(.black)

                    TextField("Ведите новое имя", text: $newUserName)
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
}

#Preview {
    ProfileView()
}

