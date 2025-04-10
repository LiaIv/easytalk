import SwiftUI

struct SimpleInfoView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Времена группы Simple")
                    .font(.title)
                    .bold()

                Text("""
                Эта группа включает в себя:
                - Present Simple
                - Past Simple
                - Future Simple

                Пример:
                I eat apples every day. (Present Simple)
                I went to school yesterday. (Past Simple)
                I will visit my grandma. (Future Simple)
                """)
                    .font(.body)
            }
            .padding()
        }
        .navigationTitle("Simple")
    }
}

#Preview {
    SimpleInfoView()
}
