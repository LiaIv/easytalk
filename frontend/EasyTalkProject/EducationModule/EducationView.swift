import SwiftUI
import Foundation

struct EducationView: View {
    let topics = [
        "Группа Simple",
        "Группа Perfect",
        "Группа Continuous",
        "Группа Perfect Continuous"
    ]
    
    var body: some View {
        NavigationStack {
            ZStack {
                Image("education_bg")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()

                VStack(spacing: 24) {
                    Text("Полезная информация")
                        .font(.system(size: 26, weight: .bold))
                        .foregroundColor(.black)
                        .padding(.horizontal, 25)
                        .padding(.vertical, 15)
                        .clipShape(Capsule())
                        .padding(.top, 70)
                    
                    Spacer().frame(height: 30)
                    
                    ForEach(topics, id: \.self) { topic in
                        if topic == "Группа Simple" {
                            NavigationLink(destination: SimpleInfoView()) {
                                topicButton(topic)
                            }
                        } else if topic == "Группа Perfect" {
                            NavigationLink(destination: PerfectInfoView()) {
                                topicButton(topic)
                            }
                        } else if topic == "Группа Continuous" {
                            NavigationLink(destination: ContinuousInfoView()) {
                                topicButton(topic)
                            }
                        } else if topic == "Группа Perfect Continuous" {
                            NavigationLink(destination: PerfectContinuousInfoView()) {
                                topicButton(topic)
                            }
                        }
                    }
                    
                    Spacer()
                }
            }
        }
    }

    // Вынесли оформление кнопки в отдельную View-функцию
    func topicButton(_ title: String) -> some View {
        Text(title)
            .font(.system(size: 20, weight: .bold))
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(Color.white.opacity(0.7))
            .foregroundColor(.black)
            .clipShape(RoundedRectangle(cornerRadius: 20))
            .padding(.horizontal, 20)
    }
}



#Preview {
    EducationView()
}
