import SwiftUI

struct PerfectContinuousInfoView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Времена группы Perfect Continuous")
                    .font(.title)
                    .bold()

                Text("""
                Эта группа включает в себя:
                - Present Perfect Continuous
                - Past Perfect Continuous
                - Future Perfect Continuous

                Пример:
                I have been working here for two years. (Present Perfect Continuous)
                She had been studying for three hours before she took a break. (Past Perfect Continuous)
                By next month, I will have been living in Moscow for five years. (Future Perfect Continuous)
                """)
                    .font(.body)
            }
            .padding()
        }
        .navigationTitle("Perfect Continuous")
    }
}

#Preview {
    PerfectContinuousInfoView()
}
