import SwiftUI

struct ContinuousInfoView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Времена группы Continuous")
                    .font(.title)
                    .bold()

                Text("""
                Эта группа включает в себя:
                - Present Continuous
                - Past Continuous
                - Future Continuous

                Пример:
                I am reading a book now. (Present Continuous)
                She was cooking dinner when I called. (Past Continuous)
                We will be traveling at this time tomorrow. (Future Continuous)
                """)
                    .font(.body)
            }
            .padding()
        }
        .navigationTitle("Continuous")
    }
}

#Preview {
    ContinuousInfoView()
}
