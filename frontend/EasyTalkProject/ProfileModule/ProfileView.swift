//
//  ProfileView.swift
//  EasyTalkProject
//
//  Created by Степан Прохоренко on 29.03.2025.
//

import SwiftUI

struct ProfileView: View {
    var body: some View {
        VStack {
            HStack(alignment: .center, spacing: 25) {
                Image("avatar")
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(width: 80, height: 80)
                    .clipShape(Circle())
                    .shadow(radius: 4)

                VStack(alignment: .leading, spacing: 8) {
                    Text("Teacher")
                        .font(.headline)
                        .foregroundColor(.black)
                        .frame(width: 225, height: 30, alignment: .leading)
                        .padding(.leading, 5)
                        .background(
                            RoundedRectangle(cornerRadius: 7)
                                .fill(Color.white.opacity(0.38))
                        )
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
    }
}

#Preview {
    ProfileView()
}
