//  Toast.swift
//  EasyTalkProject
//  Lightweight toast manager & view modifier
//
//  Created for centralized user-friendly error notifications.

import SwiftUI
import Combine

@MainActor
final class ToastManager: ObservableObject {
    @Published var message: String? = nil

    func show(_ text: String, duration: TimeInterval = 3) {
        message = text
        Task { @MainActor in
            try? await Task.sleep(nanoseconds: UInt64(duration * 1_000_000_000))
            if Task.isCancelled { return }
            withAnimation { self.message = nil }
        }
    }
}

// MARK: - View modifier
struct ToastViewModifier: ViewModifier {
    @EnvironmentObject var toast: ToastManager

    func body(content: Content) -> some View {
        ZStack {
            content
            if let msg = toast.message {
                VStack {
                    Spacer()
                    Text(msg)
                        .font(.subheadline)
                        .foregroundColor(.white)
                        .padding(.vertical, 12)
                        .padding(.horizontal, 24)
                        .background(Color.black.opacity(0.8))
                        .cornerRadius(12)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                        .padding(.bottom, 40)
                }
                .animation(.easeInOut(duration: 0.3), value: toast.message)
            }
        }
    }
}

extension View {
    /// Attach this modifier once at root to enable toast overlay.
    func toast() -> some View {
        self.modifier(ToastViewModifier())
    }
}
