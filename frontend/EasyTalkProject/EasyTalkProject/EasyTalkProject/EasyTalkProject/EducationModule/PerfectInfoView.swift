import SwiftUI

struct PerfectInfoView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Времена группы Perfect")
                    .font(.title)
                    .bold()

                Text("""
                Эта группа включает в себя:
                - Present Perfect
                - Past Perfect
                - Future Perfect

                Пример:
                I have finished my homework. (Present Perfect)
                She had left before I arrived. (Past Perfect)
                They will have built the house by summer. (Future Perfect)
                """)
                    .font(.body)
            }
            .padding()
        }
        .navigationTitle("Perfect")
    }
}

#Preview {
    PerfectInfoView()
}
