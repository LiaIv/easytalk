import SwiftUI
import Charts

/// Displays user progress statistics for the last 7 days using Swift Charts.
struct ProgressStatsView: View {
    @StateObject private var vm = ProgressStatsViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Твоя статистика (7 дней)")
                .font(.headline)

            if vm.isLoading {
                ProgressView()
            } else if let error = vm.error {
                Text(error).foregroundColor(.red)
            } else if vm.items.isEmpty {
                Text("Пока нет данных.")
                    .foregroundColor(.secondary)
            } else {
                chart
                if let summary = vm.weeklySummary {
                    Text("Всего очков за неделю: \(summary.totalWeeklyScore)")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }
        }
        .onAppear { vm.load() }
    }

    // MARK: Private views
    private var chart: some View {
        Chart(vm.items) { item in
            if let date = item.dateAsDate {
                BarMark(
                    x: .value("Date", date, unit: .day),
                    y: .value("Score", item.dailyScore)
                )
                .annotation(position: .top, alignment: .center) {
                    Text("\(item.dailyScore)")
                        .font(.caption2).foregroundColor(.primary.opacity(0.7))
                }
            }
        }
        .chartXAxis {
            AxisMarks(values: .stride(by: .day)) { value in
                if let date = value.as(Date.self) {
                    AxisGridLine()
                    AxisValueLabel(date, format: .dateTime.day().month(.narrow))
                }
            }
        }
        .frame(height: 160)
    }
}

// MARK: - ViewModel
@MainActor
final class ProgressStatsViewModel: ObservableObject {
    @Published var items: [ProgressItemResponse] = []
    @Published var weeklySummary: WeeklySummaryResponse?
    @Published var isLoading = false
    @Published var error: String?

    func load() {
        guard !isLoading else { return }
        Task {
            do {
                isLoading = true
                let resp = try await ProgressService.getProgress(days: 7)
                self.items = resp.data.sorted { $0.date < $1.date }
                self.weeklySummary = try? await ProgressService.getWeeklySummary()
            } catch {
                self.error = error.localizedDescription
            }
            isLoading = false
        }
    }
}

// MARK: - Helpers
private extension ProgressItemResponse {
    var dateAsDate: Date? {
        ISO8601DateFormatter().date(from: date)
    }
}

#Preview("StatsView") {
    ProgressStatsView()
        .padding()
}
