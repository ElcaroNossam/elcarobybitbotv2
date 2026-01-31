//
//  LinkEmailView.swift
//  EnlikoTrading
//
//  View to link email to Telegram account (Unified Auth)
//

import SwiftUI

struct LinkEmailView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var authManager: AuthManager
    
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showSuccess = false
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    VStack(spacing: 12) {
                        Image(systemName: "envelope.badge.person.crop")
                            .font(.system(size: 60))
                            .foregroundColor(.enlikoPrimary)
                        
                        Text("link_email_title".localized)
                            .font(.title2.bold())
                            .foregroundColor(.white)
                        
                        Text("link_email_description".localized)
                            .font(.subheadline)
                            .foregroundColor(.enlikoTextSecondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .padding(.top, 40)
                    
                    // Form
                    VStack(spacing: 16) {
                        // Email field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("email".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                            
                            TextField("email_placeholder".localized, text: $email)
                                .textFieldStyle(EnlikoTextFieldStyle())
                                .textInputAutocapitalization(.never)
                                .keyboardType(.emailAddress)
                                .autocorrectionDisabled()
                        }
                        
                        // Password field
                        VStack(alignment: .leading, spacing: 8) {
                            Text("password".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                            
                            SecureField("password_placeholder".localized, text: $password)
                                .textFieldStyle(EnlikoTextFieldStyle())
                        }
                        
                        // Confirm Password
                        VStack(alignment: .leading, spacing: 8) {
                            Text("confirm_password".localized)
                                .font(.caption)
                                .foregroundColor(.enlikoTextSecondary)
                            
                            SecureField("confirm_password_placeholder".localized, text: $confirmPassword)
                                .textFieldStyle(EnlikoTextFieldStyle())
                        }
                    }
                    .padding(.horizontal, 24)
                    
                    // Error message
                    if let error = errorMessage {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.enlikoRed)
                            .padding(.horizontal)
                    }
                    
                    // Link button
                    Button(action: linkEmail) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("link_email_button".localized)
                                    .fontWeight(.semibold)
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isFormValid ? Color.enlikoPrimary : Color.gray)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .disabled(!isFormValid || isLoading)
                    .padding(.horizontal, 24)
                    
                    Spacer()
                }
            }
        }
        .navigationTitle("link_email".localized)
        .navigationBarTitleDisplayMode(.inline)
        .alert("success".localized, isPresented: $showSuccess) {
            Button("common_ok".localized) {
                dismiss()
            }
        } message: {
            Text("link_email_success".localized)
        }
    }
    
    // MARK: - Validation
    private var isFormValid: Bool {
        !email.isEmpty &&
        email.contains("@") &&
        password.count >= 6 &&
        password == confirmPassword
    }
    
    // MARK: - Link Email Action
    private func linkEmail() {
        guard isFormValid else { return }
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                struct LinkEmailRequest: Encodable {
                    let email: String
                    let password: String
                }
                
                struct LinkResponse: Codable {
                    let success: Bool
                    let message: String?
                }
                
                let request = LinkEmailRequest(email: email.lowercased(), password: password)
                let response: LinkResponse = try await NetworkService.shared.post(
                    "/auth/telegram/link-email",
                    body: request
                )
                
                await MainActor.run {
                    isLoading = false
                    if response.success {
                        showSuccess = true
                        // Refresh user data
                        Task {
                            await authManager.fetchCurrentUser()
                        }
                    } else {
                        errorMessage = response.message ?? "link_email_error".localized
                    }
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
}

// MARK: - Text Field Style
struct EnlikoTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding()
            .background(Color.enlikoCard)
            .foregroundColor(.white)
            .cornerRadius(10)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color.enlikoBorder, lineWidth: 1)
            )
    }
}

#Preview {
    NavigationStack {
        LinkEmailView()
            .environmentObject(AuthManager.shared)
    }
    .preferredColorScheme(.dark)
}
