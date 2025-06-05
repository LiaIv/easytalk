import SwiftUI

struct WrapWordsView: View {
    let words: [String]
    @Binding var userSentence: [String]
    let onWordTap: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading) {
            let columns = [GridItem(.adaptive(minimum: 80))]
            LazyVGrid(columns: columns, spacing: 10) {
                ForEach(words, id: \.self) { word in
                    Text(word)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color.blue.opacity(0.3))
                        .cornerRadius(8)
                        .onTapGesture {
                            onWordTap(word)
                        }
                }
            }
        }
    }
}
