//
//  LoginView.swift
//  LyxenTrading
//
//  Authentication screen with localization
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authManager: AuthManager
    @ObservedObject var localization = LocalizationManager.shared
    
    @State private var email = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var showVerification = false
    @State private var verificationCode = ""
    @State private var firstName = ""
    @State private var lastName = ""
    
    // Demo mode
    @State private var showDemoAlert = false
    @State private var demoUserId = ""
    
    var body: some View {
        NavigationStack {
            ZStack {
                // Background gradient
                LinearGradient(
                    colors: [Color.lyxenBackground, Color.lyxenSurface],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 32) {
                        // Language Picker at top
                        HStack {
                            Spacer()
                            CompactLanguagePicker()
                        }
                        .padding(.horizontal)
                        
                        // Logo
                        logoSection
                        
                        // Form
                        if showVerification {
                            verificationSection
                        } else {
                            authFormSection
                        }
                        
                        // Demo Login (for development)
                        #if DEBUG
                        demoSection
                        #endif
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 20)
                }
            }
            .withRTLSupport()
            .alert("common_error".localized, isPresented: .constant(authManager.errorMessage != nil)) {
                Button("common_ok".localized) { authManager.clearError() }
            } message: {
                Text(authManager.errorMessage ?? "")
            }
            .alert("Demo Login", isPresented: $showDemoAlert) {
                TextField("User ID", text: $demoUserId)
                    .keyboardType(.numberPad)
                Button("Login") {
                    if let userId = Int(demoUserId) {
                        Task {
                            await authManager.loginAsDemo(userId: userId)
                        }
                    }
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("Enter your Telegram User ID for demo access")
            }
        }
    }
    
    // MARK: - Logo Section
    private var logoSection: some View {
        VStack(spacing: 16) {
            // App Icon
            ZStack {
                Circle()
                    .fill(Color.lyxenGradient)
                    .frame(width: 100, height: 100)
                
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .font(.system(size: 44))
                    .foregroundColor(.white)
            }
            .shadow(color: Color.lyxenPrimary.opacity(0.5), radius: 20)
            
            Text("LYXEN")
                .font(.system(size: 36, weight: .bold, design: .rounded))
                .foregroundColor(.white)
            
            Text("auth_welcome".localized)
                .font(.subheadline)
                .foregroundColor(.lyxenTextSecondary)
        }
    }
    
    // MARK: - Auth Form Section
    private var authFormSection: some View {
        VStack(spacing: 20) {
            // Email Field
            LyxenTextField(
                icon: "envelope.fill",
                placeholder: "auth_email".localized,
                text: $email
            )
            .keyboardType(.emailAddress)
            .textInputAutocapitalization(.never)
            
            // Password Field
            LyxenSecureField(
                icon: "lock.fill",
                placeholder: "auth_password".localized,
                text: $password
            )
            
            // Name fields for registration
            if isRegistering {
                HStack(spacing: 12) {
                    LyxenTextField(
                        icon: "person.fill",
                        placeholder: "First Name",
                        text: $firstName
                    )
                    
                    LyxenTextField(
                        icon: "person.fill",
                        placeholder: "Last Name",
                        text: $lastName
                    )
                }
            }
            
            // Submit Button
            Button(action: submitForm) {
                HStack {
                    if authManager.isLoading {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Text(isRegistering ? "auth_register".localized : "auth_login".localized)
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.lyxenGradient)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(authManager.isLoading || email.isEmpty || password.isEmpty)
            
            // Toggle Register/Login
            Button(action: { isRegistering.toggle() }) {
                Text(isRegistering ? "Already have an account? Sign In" : "Don't have an account? Register")
                    .font(.subheadline)
                    .foregroundColor(.lyxenPrimary)
            }
        }
        .lyxenCard()
        .padding(20)
    }
    
    // MARK: - Verification Section
    private var verificationSection: some View {
        VStack(spacing: 20) {
            Text("Verify Your Email")
                .font(.title2.bold())
                .foregroundColor(.white)
            
            Text("We sent a code to \(email)")
                .font(.subheadline)
                .foregroundColor(.lyxenTextSecondary)
            
            LyxenTextField(
                icon: "number",
                placeholder: "Verification Code",
                text: $verificationCode
            )
            .keyboardType(.numberPad)
            
            Button(action: verifyEmail) {
                HStack {
                    if authManager.isLoading {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Text("Verify")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.lyxenGradient)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(verificationCode.count < 4)
            
            Button("Back") {
                showVerification = false
            }
            .foregroundColor(.lyxenTextSecondary)
        }
        .lyxenCard()
        .padding(20)
    }
    
    // MARK: - Demo Section
    private var demoSection: some View {
        VStack(spacing: 12) {
            Divider()
                .background(Color.lyxenTextMuted)
            
            Text("Development Mode")
                .font(.caption)
                .foregroundColor(.lyxenTextMuted)
            
            Button(action: { showDemoAlert = true }) {
                HStack {
                    Image(systemName: "play.circle.fill")
                    Text("Demo Login")
                }
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(Color.lyxenCard)
                .foregroundColor(.lyxenPrimary)
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.lyxenPrimary.opacity(0.5), lineWidth: 1)
                )
            }
        }
    }
    
    // MARK: - Actions
    private func submitForm() {
        Task {
            if isRegistering {
                let success = await authManager.registerWithEmail(
                    email: email,
                    password: password,
                    firstName: firstName.isEmpty ? nil : firstName,
                    lastName: lastName.isEmpty ? nil : lastName
                )
                if success {
                    showVerification = true
                }
            } else {
                _ = await authManager.loginWithEmail(email: email, password: password)
            }
        }
    }
    
    private func verifyEmail() {
        Task {
            await authManager.verifyEmail(email: email, code: verificationCode)
        }
    }
}

// MARK: - Custom Text Fields
struct LyxenTextField: View {
    let icon: String
    let placeholder: String
    @Binding var text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.lyxenTextSecondary)
                .frame(width: 20)
            
            TextField(placeholder, text: $text)
                .foregroundColor(.white)
        }
        .padding()
        .background(Color.lyxenSurface)
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(Color.lyxenCardHover, lineWidth: 1)
        )
    }
}

struct LyxenSecureField: View {
    let icon: String
    let placeholder: String
    @Binding var text: String
    @State private var isSecure = true
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(.lyxenTextSecondary)
                .frame(width: 20)
            
            if isSecure {
                SecureField(placeholder, text: $text)
                    .foregroundColor(.white)
            } else {
                TextField(placeholder, text: $text)
                    .foregroundColor(.white)
            }
            
            Button(action: { isSecure.toggle() }) {
                Image(systemName: isSecure ? "eye.slash" : "eye")
                    .foregroundColor(.lyxenTextSecondary)
            }
        }
        .padding()
        .background(Color.lyxenSurface)
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(Color.lyxenCardHover, lineWidth: 1)
        )
    }
}

#Preview {
    LoginView()
        .environmentObject(AuthManager.shared)
        .preferredColorScheme(.dark)
}
