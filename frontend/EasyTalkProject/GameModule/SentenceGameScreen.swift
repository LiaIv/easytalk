import SwiftUI

extension View {
   func hideCustomTabBar() -> some View {
       self.modifier(HideCustomTabBarModifier())
   }
}

struct HideCustomTabBarModifier: ViewModifier {
   func body(content: Content) -> some View {
       content
           .background(HideTabBarHelper())
   }
}

struct HideTabBarHelper: UIViewControllerRepresentable {
   func makeUIViewController(context: Context) -> UIViewController {
       let controller = UIViewController()
       controller.view.backgroundColor = .clear
       controller.view.isUserInteractionEnabled = false
       controller.hidesBottomBarWhenPushed = true
       return controller
   }

   func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

struct WrapWordsViewCustom: View {
   let words: [String]
   @Binding var userSentence: [String]
   let onWordTap: (String) -> Void

   var body: some View {
       VStack {
           let columns = [GridItem(.adaptive(minimum: 80))]
           LazyVGrid(columns: columns, spacing: 10) {
               ForEach(words, id: \.self) { word in
                   Text(word)
                       .padding()
                       .background(Color(red: 214/255, green: 228/255, blue: 240/255))
                       .cornerRadius(10)
                       .onTapGesture {
                           if !userSentence.contains(word) {
                               DispatchQueue.main.async {
                                   onWordTap(word)
                               }
                           }
                       }
                       .transition(.scale)
                       .animation(.spring(), value: words)
               }
           }
       }
   }
}

enum LanguageLevel {
   case beginner
   case preIntermediate
   case intermediate
}

struct SentenceGameScreen: View {
   @State private var hasMadeMistake: Bool = false
   @State private var currentIndex: Int = 0
   @State private var correctSentence: String = ""
   @State private var shuffledWords: [String] = []
   @State private var userSentence: [String] = []
   @State private var showNext: Bool = false
   @State private var message: String = ""
   @Environment(\.dismiss) private var dismiss
   @State private var progressColors: [Color] = Array(repeating: .gray, count: 10)
   @State private var flashColor: Color? = nil
   @State private var showHint: Bool = false
   @State private var showErrorHint: Bool = false

   @State private var currentLevel: LanguageLevel = .beginner

   var beginnerSentences: [String] = [
       "I have a dog",
       "She is my mother",
       "This is my pen",
       "We like apples",
       "He is a teacher",
       "The sky is blue",
       "I am very happy",
       "My name is Jack",
       "They are good people",
       "I like this game"
   ]

   var preIntermediateSentences: [String] = [
       "I eat breakfast every morning",
       "She is writing a message now",
       "We visited the zoo last week",
       "They are watching a movie together",
       "He never eats fast food",
       "My friend works in a bank",
       "It was hot in the summer",
       "I want to learn Spanish",
       "We are going to Paris tomorrow",
       "She speaks English very well"
   ]

   var intermediateSentences: [String] = [
       "If you study hard you will pass the test",
       "She has lived in London for ten years",
       "I wish I had more free time",
       "They had eaten dinner before we arrived",
       "You should check the answer before sending",
       "Although he was late he finished the task",
       "We might visit the museum next week",
       "The book was so boring we stopped reading",
       "He promised he would call in the evening",
       "By the time we arrived the meeting had started"
   ]
   
   var beginnerHints: [String] = [
       "Начни с \"I\" — это подлежащее (тот, кто что-то делает). Глагол \"have\" означает «иметь». Далее укажи объект — \"a dog\", где \"a\" — неопределённый артикль перед единичным предметом.",
       "Подлежащее — \"She\". Для описания состояния или роли (например, кем она приходится) используется глагол-связка \"is\". Далее указываем, кто она — \"my mother\".",
       "Фраза \"This is\" используется, чтобы представить предмет. Потом говорим, чей он — \"my pen\". Обрати внимание: нет артикля, потому что используется притяжательное местоимение (\"my\").",
       "Подлежащее — \"We\". Глагол \"like\" (нравится) идет в базовой форме, так как \"we\" — множественное число. Далее — объект, что нам нравится — \"apples\".",
       "Подлежащее — \"He\", потом \"is\" (глагол «быть» в настоящем времени). Перед профессией нужно поставить артикль \"a\", так как профессия — это исчисляемое существительное в единственном числе.",
       "\"The sky\" — подлежащее. Для описания цвета или состояния используем \"is\", а \"blue\" — прилагательное, описывающее, какой небо.",
       "С местоимением \"I\" используется форма \"am\" от глагола «быть». Далее — усилитель \"very\" и прилагательное \"happy\".",
       "Подлежащее — \"My name\". Используем связку \"is\" для связывания с именем — \"Jack\". Это устойчивое выражение для представления.",
       "\"They\" требует форму \"are\" (множественное число глагола «быть»). Далее — прилагательное \"good\" и существительное \"people\", которое уже во множественном числе — артикль не нужен.",
       "Стандартная структура выражения предпочтения: \"I like...\". Далее — то, что нравится: \"this game\". \"This\" показывает, что игра близка или известна собеседнику."
   ]

   var preIntermediateHints: [String] = [
       "Повседневные действия = Present Simple. Подлежащее \"I\", глагол \"eat\" в базовой форме. Частотное выражение \"every morning\" ставим в конец.",
       "Действие происходит сейчас — это Present Continuous: \"She\" + \"is\" + глагол с -ing (\"writing\"). \"Now\" подтверждает текущее время.",
       "В прошедшем времени используем вторую форму глагола: \"visited\". Подлежащее — \"We\". \"Last week\" — указатель Past Simple.",
       "Сейчас = Present Continuous: \"are watching\". \"Together\" — обстоятельство, указывающее, как они это делают.",
       "Наречия частоты (например, \"never\") ставятся перед смысловым глаголом (\"eats\"). Не забудь добавить -s, так как подлежащее — \"He\".",
       "Подлежащее — \"My friend\" (3-е лицо ед. ч.), значит, глагол \"work\" получает окончание -s. Уточняем, где он работает — \"in a bank\".",
       "Описание погоды в прошлом — используем \"It was\" (Past Simple от \"to be\"). Далее — прилагательное \"hot\" и указание времени — \"in the summer\".",
       "После глагола \"want\" обязательно используем \"to + глагол\" (инфинитив): \"to learn\". Уточняем, что именно — Spanish.",
       "Ближайшее будущее по плану = \"be going to\": \"We are going to\". Далее указываем направление — \"Paris\" и время — \"tomorrow\".",
       "Подлежащее — \"She\", значит к глаголу \"speak\" добавляем -s: \"speaks\". Наречие \"very well\" (как именно?) ставим в конец предложения."
   ]

   var intermediateHints: [String] = [
       "Это условное предложение 1 типа: в первой части — Present Simple (\"study\"), во второй — Future Simple (\"will pass\").",
       "Используем Present Perfect: действие началось в прошлом и продолжается до сих пор. \"Has lived\" + указание продолжительности (for ten years).",
       "Конструкция \"I wish I had...\" выражает сожаление о настоящем (не хватает времени сейчас), поэтому используем Past Simple — \"had\".",
       "Два действия в прошлом: первое (ужин) — в Past Perfect (had eaten), второе — в Past Simple (arrived). Это важно для правильного порядка событий.",
       "После модального глагола \"should\" идет инфинитив без \"to\" — \"check\". Порядок слов: сначала совет, потом уточнение — \"before sending\".",
       "После \"Although\" сохраняется обычный порядок слов: подлежащее + глагол (he was late). Вторая часть — результат — \"he finished...\".",
       "После модального глагола \"might\" идет инфинитив без \"to\" — \"visit\". Уточни время действия: \"next week\".",
       "Конструкция \"so + прилагательное\" (so boring) показывает причину. Вторая часть — результат: \"we stopped reading\".",
       "Это косвенная речь. Вместо кавычек — структура: \"He promised he would...\" + глагол. \"Would\" заменяет \"will\" в прошедшем времени.",
       "Когда мы прибыли (Past Simple), встреча уже началась (Past Perfect). Слова \"By the time\" требуют использования Past Perfect для более раннего действия."
   ]

   
   var currentHint: String {
       switch currentLevel {
       case .beginner:
           return beginnerHints[currentIndex]
       case .preIntermediate:
           return preIntermediateHints[currentIndex]
       case .intermediate:
           return intermediateHints[currentIndex]
       }
   }


   var selectedSentences: [String] {
       switch currentLevel {
       case .beginner:
           return beginnerSentences
       case .preIntermediate:
           return preIntermediateSentences
       case .intermediate:
           return intermediateSentences
       }
   }

   var body: some View {
       ZStack {
           (flashColor ?? Color(red: 230/255, green: 245/255, blue: 255/255))
               .ignoresSafeArea()
               .animation(.easeInOut(duration: 0.3), value: flashColor)

           VStack(spacing: 20) {
               // Лампочка справа вверху
               HStack {
                   Spacer()
                       .toolbar {
                           ToolbarItem(placement: .navigationBarTrailing) {
                               Button(action: {
                                   showHint = true
                               }) {
                                   Image(systemName: "lightbulb.fill")
                                       .foregroundColor(.yellow)
                               }
                           }
                       }
               }

               HStack(spacing: 10) {
                   ForEach(0..<10, id: \.self) { index in
                       Circle()
                           .fill(progressColors[index])
                           .frame(width: 20, height: 20)
                           .overlay(
                               Circle()
                                   .stroke(Color.black.opacity(0.5), lineWidth: 1)
                           )
                   }
               }

               Text("Составь предложение")
                   .font(.title)
                   .transition(.opacity.combined(with: .slide))
                   .animation(.easeInOut(duration: 0.4), value: userSentence)

               ZStack(alignment: .leading) {
                   RoundedRectangle(cornerRadius: 10)
                       .fill(Color.gray.opacity(0.2))
                       .frame(height: 250)

                   if userSentence.isEmpty {
                       Text("Нажми на слово для добавления")
                           .foregroundColor(.gray)
                           .padding(.leading)
                   } else {
                       VStack(alignment: .leading) {
                           let columns = [GridItem(.adaptive(minimum: 80))]
                           LazyVGrid(columns: columns, spacing: 10) {
                               ForEach(userSentence, id: \.self) { word in
                                   Text(word)
                                       .padding(.horizontal, 10)
                                       .padding(.vertical, 5)
                                       .background(Color.green.opacity(0.3))
                                       .cornerRadius(8)
                                       .transition(.scale.combined(with: .opacity))
                                       .animation(.spring(), value: userSentence)
                               }
                           }
                           .padding()
                       }
                   }
               }
               .padding(.horizontal)

               HStack {
                   Button("Очистить") {
                       withAnimation {
                           shuffledWords += userSentence
                           userSentence.removeAll()
                       }
                   }
                   .padding()
                   .background(Color.red.opacity(0.2))
                   .cornerRadius(10)

                   Button("Готово") {
                       checkSentence()
                   }
                   .disabled(userSentence.count != correctSentence.components(separatedBy: " ").count)
                   .padding()
                   .background(Color.blue.opacity(0.2))
                   .cornerRadius(10)
               }

               Spacer()

               WrapWordsViewCustom(words: shuffledWords, userSentence: $userSentence, onWordTap: { word in
                   withAnimation(.spring()) {
                       userSentence.append(word)
                       shuffledWords.removeAll { $0 == word }
                   }
               })
               .padding()
           }
           .padding()
       }
       .onAppear {
           loadNewSentence()
       }
       .alert(isPresented: $showNext) {
           Alert(
               title: Text(currentIndex + 1 < selectedSentences.count ? "Следующее предложение." : "Ты завершил игру."),
               message: Text(message),
               dismissButton: .default(Text("OK")) {
                   if currentIndex + 1 < selectedSentences.count {
                       currentIndex += 1
                       hasMadeMistake = false
                       loadNewSentence()
                   } else {
                       dismiss()
                   }
               }
           )
       }
       
       // Подсказка при нажатии на лампочку
       .alert("Подсказка", isPresented: $showHint) {
           Button("OK", role: .cancel) { }
       } message: {
           Text(currentHint)
       }
       // Подсказка при ошибке
       .alert("Попробуй ещё раз", isPresented: $showErrorHint) {
           Button("OK", role: .cancel) { }
       } message: {
           Text(currentHint)
       }
   }

   func loadNewSentence() {
       let sentence = selectedSentences[currentIndex]
       correctSentence = sentence.trimmingCharacters(in: .punctuationCharacters)
       shuffledWords = correctSentence.components(separatedBy: " ").shuffled()
       userSentence = []
   }

   func checkSentence() {
          let user = userSentence.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
          let isCorrect = user == correctSentence

          if !isCorrect {
              hasMadeMistake = true
              message = "Не верно."
              flashColor = Color.red.opacity(0.3)
              showErrorHint = true

              withAnimation {
                  shuffledWords += userSentence
                  userSentence.removeAll()
              }

              if progressColors[currentIndex] == .gray {
                  progressColors[currentIndex] = .red
              }
          }
          else {
              message = "Верно!"
              flashColor = Color.green.opacity(0.3)

              if !hasMadeMistake {
                  progressColors[currentIndex] = .green
              }

              showNext = true
          }

          DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
              flashColor = nil
          }
      }

}


#Preview {
   SentenceGameScreen()
}
