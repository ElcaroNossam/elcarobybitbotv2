//
//  DisclaimerView.swift
//  EnlikoTrading
//
//  Legal disclaimer screen - REQUIRED for compliance
//  Must be shown on first launch before accessing any features
//

import SwiftUI

struct DisclaimerView: View {
    @EnvironmentObject var authManager: AuthManager
    @ObservedObject var localization = LocalizationManager.shared
    
    // Closures for accept/decline actions
    var onAccept: () -> Void
    var onDecline: () -> Void
    
    @State private var isLoading = false
    
    var body: some View {
        ZStack {
            // Background
            LinearGradient(
                colors: [Color.enlikoBackground, Color.enlikoSurface],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 24) {
                    // Warning Icon
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.orange)
                        .padding(.top, 40)
                    
                    // Title
                    Text("disclaimer_title".localized)
                        .font(.title)
                        .fontWeight(.bold)
                        .multilineTextAlignment(.center)
                    
                    // Disclaimer Content
                    disclaimerContent
                    
                    // Bullet Points
                    bulletPoints
                    
                    // Risk Warning
                    riskWarning
                    
                    Spacer(minLength: 40)
                    
                    // Accept Button
                    acceptButton
                    
                    // Decline Button
                    declineButton
                    
                    // Legal Footer
                    legalFooter
                }
                .padding(.horizontal, 24)
            }
        }
        .withRTLSupport()
    }
    
    // MARK: - Disclaimer Content
    
    private var disclaimerContent: some View {
        VStack(spacing: 16) {
            Text("disclaimer_intro".localized)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            Divider()
        }
    }
    
    private var bulletPoints: some View {
        VStack(alignment: .leading, spacing: 12) {
            DisclaimerBullet(
                icon: "xmark.circle.fill",
                color: .red,
                text: "disclaimer_not_financial_advice".localized
            )
            
            DisclaimerBullet(
                icon: "chart.line.downtrend.xyaxis",
                color: .orange,
                text: "disclaimer_risk_of_loss".localized
            )
            
            DisclaimerBullet(
                icon: "clock.arrow.circlepath",
                color: .yellow,
                text: "disclaimer_past_performance".localized
            )
            
            DisclaimerBullet(
                icon: "person.fill.checkmark",
                color: .blue,
                text: "disclaimer_user_responsibility".localized
            )
            
            DisclaimerBullet(
                icon: "graduationcap.fill",
                color: .purple,
                text: "disclaimer_educational_only".localized
            )
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(16)
    }
    
    private var riskWarning: some View {
        VStack(spacing: 8) {
            Text("⚠️ " + "disclaimer_risk_warning_title".localized)
                .font(.headline)
                .foregroundColor(.red)
            
            Text("disclaimer_risk_warning_text".localized)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .background(Color.red.opacity(0.1))
        .cornerRadius(12)
    }
    
    private var acceptButton: some View {
        Button(action: acceptDisclaimer) {
            HStack {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Image(systemName: "checkmark.circle.fill")
                    Text("disclaimer_accept_btn".localized)
                }
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.enlikoGreen)
            .foregroundColor(.white)
            .cornerRadius(12)
            .font(.headline)
        }
        .disabled(isLoading)
    }
    
    private var declineButton: some View {
        Button(action: declineDisclaimer) {
            Text("disclaimer_decline_btn".localized)
                .frame(maxWidth: .infinity)
                .padding()
                .foregroundColor(.secondary)
                .font(.subheadline)
        }
    }
    
    private var legalFooter: some View {
        VStack(spacing: 8) {
            Text("disclaimer_terms_agreement".localized)
                .font(.caption2)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            HStack(spacing: 16) {
                if let termsURL = URL(string: "https://enliko.com/terms.html") {
                    Link("legal_terms".localized, destination: termsURL)
                        .font(.caption2)
                }
                
                if let privacyURL = URL(string: "https://enliko.com/privacy.html") {
                    Link("legal_privacy".localized, destination: privacyURL)
                        .font(.caption2)
                }
            }
        }
        .padding(.bottom, 32)
    }
    
    // MARK: - Actions
    
    private func acceptDisclaimer() {
        isLoading = true
        
        // Save disclaimer acceptance
        UserDefaults.standard.set(true, forKey: "disclaimerAccepted")
        UserDefaults.standard.set(Date(), forKey: "disclaimerAcceptedDate")
        
        // Notify server (optional, best effort)
        Task {
            do {
                try await NetworkService.shared.postIgnoreResponse(
                    "/users/disclaimer",
                    body: ["accepted": true]
                )
            } catch {
                // Continue anyway - local acceptance is enough
                print("Failed to sync disclaimer acceptance: \(error)")
            }
            
            await MainActor.run {
                isLoading = false
                onAccept()
            }
        }
    }
    
    private func declineDisclaimer() {
        // Call decline closure
        onDecline()
    }
}

// MARK: - Bullet Point Component

struct DisclaimerBullet: View {
    let icon: String
    let color: Color
    let text: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(color)
                .frame(width: 24)
            
            Text(text)
                .font(.subheadline)
                .foregroundColor(.primary)
            
            Spacer()
        }
    }
}

// MARK: - Preview

#Preview {
    DisclaimerView(
        onAccept: { print("Accepted") },
        onDecline: { print("Declined") }
    )
    .environmentObject(AuthManager.shared)
}
