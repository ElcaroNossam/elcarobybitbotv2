//
//  LoginView.swift
//  EnlikoTrading
//
//  Authentication: Email (primary) + Telegram 2FA (secondary option)
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authManager: AuthManager
    @ObservedObject var localization = LocalizationManager.shared
    
    // Auth mode
    @State private var showTelegramLogin = false
    @State private var showLinkEmail = false  // After TG login, prompt to add email
    
    // Email auth (primary)
    @State private var email = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var showVerification = false
    @State private var verificationCode = ""
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var telegramUsernameReg = ""  // Optional TG username for registration
    @State private var passwordError = ""
    @State private var emailError = ""
    
    // Telegram 2FA auth (secondary)
    @State private var telegramUsername = ""
    @State private var requestId: String? = nil
    @State private var isWaitingFor2FA = false
    @State private var twoFAError = ""
    @State private var pollingTimer: Timer? = nil
    
    // Demo mode
    @State private var showDemoAlert = false
    @State private var demoUserId = ""
    
    var body: some View {
        NavigationStack {
            ZStack {
                LinearGradient(
                    colors: [Color.enlikoBackground, Color.enlikoSurface],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        HStack {
                            Spacer()
                            CompactLanguagePicker()
                        }
                        .padding(.horizontal)
                        
                        logoSection
                        
                        // Priority flow: Verification > Link Email > Telegram 2FA > Email Form
                        if showVerification {
                            verificationSection
                        } else if showLinkEmail {
                            linkEmailSection
                        } else if isWaitingFor2FA {
                            waiting2FASection
                        } else if showTelegramLogin {
                            telegramLoginSection
                        } else {
                            emailFormSection
                        }
                        
                        #if DEBUG
                        demoSection
                        #endif
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 20)
                    .padding(.bottom, 40)
                }
            }
            .withRTLSupport()
            .alert("common_error".localized, isPresented: Binding(
                get: { authManager.errorMessage != nil },
                set: { if !$0 { authManager.clearError() } }
            )) {
                Button("common_ok".localized) { authManager.clearError() }
            } message: {
                Text(authManager.errorMessage ?? "")
            }
            .alert("Demo Login", isPresented: $showDemoAlert) {
                TextField("User ID", text: $demoUserId)
                    .keyboardType(.numberPad)
                Button("Login") {
                    if let userId = Int(demoUserId) {
                        Task { await authManager.loginAsDemo(userId: userId) }
                    }
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("Enter your Telegram User ID for demo access")
            }
            .onDisappear {
                stopPolling()
            }
        }
    }
    
    // MARK: - Logo Section
    private var logoSection: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(Color.enlikoGradient)
                    .frame(width: 100, height: 100)
                
                Image(systemName: "chart.line.uptrend.xyaxis")
                    .font(.system(size: 44))
                    .foregroundColor(.white)
            }
            .shadow(color: Color.enlikoPrimary.opacity(0.5), radius: 20)
            
            Text("ENLIKO")
                .font(.system(size: 36, weight: .bold, design: .rounded))
                .foregroundColor(.white)
            
            Text("auth_welcome".localized)
                .font(.subheadline)
                .foregroundColor(.enlikoTextSecondary)
        }
    }
    
    // MARK: - Email Form Section (PRIMARY)
    private var emailFormSection: some View {
        VStack(spacing: 20) {
            // Title
            VStack(spacing: 8) {
                Text(isRegistering ? "auth_create_account".localized : "auth_login_title".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                
                Text(isRegistering ? "auth_register_subtitle".localized : "auth_login_subtitle".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                    .multilineTextAlignment(.center)
            }
            
            // Registration extra fields
            if isRegistering {
                HStack(spacing: 12) {
                    EnlikoTextField(icon: "person", placeholder: "auth_first_name".localized, text: $firstName)
                    EnlikoTextField(icon: "person", placeholder: "auth_last_name".localized, text: $lastName)
                }
                
                // Optional Telegram username
                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: 8) {
                        Image(systemName: "paperplane.fill")
                            .font(.subheadline)
                            .foregroundColor(.enlikoTextSecondary)
                        TextField("@username", text: $telegramUsernameReg)
                            .foregroundColor(.white)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                    }
                    .padding()
                    .background(Color.enlikoSurface)
                    .cornerRadius(10)
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .stroke(Color.enlikoCardHover, lineWidth: 1)
                    )
                    
                    Text("auth_telegram_optional_hint".localized)
                        .font(.caption)
                        .foregroundColor(.enlikoTextMuted)
                        .padding(.leading, 4)
                }
            }
            
            // Email field
            VStack(alignment: .leading, spacing: 4) {
                EnlikoTextField(icon: "envelope", placeholder: "auth_email_placeholder".localized, text: $email)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .onChange(of: email) { _, _ in validateEmail() }
                
                if !emailError.isEmpty {
                    Text(emailError)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.horizontal, 4)
                }
            }
            
            // Password field
            VStack(alignment: .leading, spacing: 4) {
                EnlikoSecureField(icon: "lock", placeholder: "auth_password_placeholder".localized, text: $password)
                    .textContentType(isRegistering ? .newPassword : .password)
                    .onChange(of: password) { _, _ in validatePassword() }
                
                if !passwordError.isEmpty {
                    Text(passwordError)
                        .font(.caption)
                        .foregroundColor(.orange)
                        .padding(.horizontal, 4)
                }
            }
            
            // Submit button
            Button(action: submitEmailForm) {
                HStack {
                    if authManager.isLoading {
                        ProgressView().tint(.white)
                    } else {
                        Text(isRegistering ? "auth_register_button".localized : "auth_login_button".localized)
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 54)
                .background(
                    isFormValid 
                        ? Color.enlikoGradient 
                        : LinearGradient(colors: [.gray.opacity(0.4), .gray.opacity(0.3)], startPoint: .leading, endPoint: .trailing)
                )
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(!isFormValid || authManager.isLoading)
            
            // Toggle login/register
            Button(action: { isRegistering.toggle() }) {
                Text(isRegistering ? "auth_have_account".localized : "auth_no_account".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoPrimary)
            }
            
            // Divider
            HStack {
                Rectangle()
                    .fill(Color.enlikoTextMuted.opacity(0.3))
                    .frame(height: 1)
                
                Text("auth_or".localized)
                    .font(.caption)
                    .foregroundColor(.enlikoTextMuted)
                    .padding(.horizontal, 12)
                
                Rectangle()
                    .fill(Color.enlikoTextMuted.opacity(0.3))
                    .frame(height: 1)
            }
            .padding(.top, 8)
            
            // Telegram 2FA option (SECONDARY)
            Button(action: { showTelegramLogin = true }) {
                HStack(spacing: 12) {
                    Image(systemName: "paperplane.fill")
                        .font(.title3)
                    Text("auth_login_with_telegram".localized)
                        .fontWeight(.medium)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.enlikoCard)
                .foregroundColor(.white)
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color(red: 0, green: 0.53, blue: 0.8).opacity(0.5), lineWidth: 1)
                )
            }
            
            Text("auth_telegram_option_hint".localized)
                .font(.caption)
                .foregroundColor(.enlikoTextMuted)
                .multilineTextAlignment(.center)
        }
        .enlikoCard()
        .padding(20)
    }
    
    // MARK: - Telegram Login Section (SECONDARY)
    private var telegramLoginSection: some View {
        VStack(spacing: 24) {
            // Header with back button
            HStack {
                Button(action: { showTelegramLogin = false }) {
                    Image(systemName: "chevron.left")
                        .font(.title3)
                        .foregroundColor(.enlikoPrimary)
                }
                Spacer()
                Text("auth_telegram_login_title".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                // Placeholder for balance
                Image(systemName: "chevron.left")
                    .font(.title3)
                    .opacity(0)
            }
            
            VStack(spacing: 8) {
                Text("auth_telegram_login_subtitle".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                    .multilineTextAlignment(.center)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 12) {
                    Text("@")
                        .font(.title2)
                        .foregroundColor(.enlikoTextSecondary)
                        .frame(width: 24)
                    
                    TextField("username", text: $telegramUsername)
                        .foregroundColor(.white)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.enlikoCardHover, lineWidth: 1)
                )
                
                if !twoFAError.isEmpty {
                    Text(twoFAError)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.horizontal, 4)
                }
            }
            
            Button(action: request2FALogin) {
                HStack(spacing: 12) {
                    if authManager.isLoading {
                        ProgressView()
                            .tint(.white)
                    } else {
                        Image(systemName: "paperplane.fill")
                            .font(.title3)
                        Text("auth_send_confirmation".localized)
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 56)
                .background(
                    isUsernameValid
                        ? LinearGradient(
                            colors: [Color(red: 0, green: 0.53, blue: 0.8), Color(red: 0, green: 0.67, blue: 0.87)],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                        : LinearGradient(colors: [.gray.opacity(0.4), .gray.opacity(0.3)], startPoint: .leading, endPoint: .trailing)
                )
                .foregroundColor(.white)
                .cornerRadius(14)
            }
            .disabled(!isUsernameValid || authManager.isLoading)
            
            Text("auth_telegram_hint".localized)
                .font(.caption)
                .foregroundColor(.enlikoTextMuted)
                .multilineTextAlignment(.center)
        }
        .enlikoCard()
        .padding(20)
    }
    
    // MARK: - Waiting for 2FA Confirmation
    private var waiting2FASection: some View {
        VStack(spacing: 24) {
            HStack {
                Button(action: { 
                    stopPolling()
                    isWaitingFor2FA = false 
                }) {
                    Image(systemName: "chevron.left")
                        .font(.title3)
                        .foregroundColor(.enlikoPrimary)
                }
                Spacer()
                Text("auth_confirm_in_telegram".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "chevron.left")
                    .font(.title3)
                    .opacity(0)
            }
            
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(red: 0, green: 0.53, blue: 0.8), Color(red: 0, green: 0.67, blue: 0.87)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 100, height: 100)
                
                Image(systemName: "bell.badge.fill")
                    .font(.system(size: 44))
                    .foregroundColor(.white)
            }
            .shadow(color: Color(red: 0, green: 0.53, blue: 0.8).opacity(0.5), radius: 15)
            
            VStack(spacing: 12) {
                Text("auth_waiting_confirmation".localized)
                    .font(.title3.bold())
                    .foregroundColor(.white)
                
                Text("auth_check_telegram".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                    .multilineTextAlignment(.center)
                
                // Animated dots
                HStack(spacing: 8) {
                    ForEach(0..<3) { i in
                        Circle()
                            .fill(Color.enlikoPrimary)
                            .frame(width: 10, height: 10)
                            .opacity(0.7)
                            .animation(
                                Animation.easeInOut(duration: 0.5)
                                    .repeatForever(autoreverses: true)
                                    .delay(Double(i) * 0.2),
                                value: isWaitingFor2FA
                            )
                    }
                }
                .padding(.top, 8)
                
                if !twoFAError.isEmpty {
                    Text(twoFAError)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.top, 8)
                }
            }
            
            Button(action: openTelegramApp) {
                HStack(spacing: 12) {
                    Image(systemName: "arrow.up.forward.app.fill")
                    Text("auth_open_telegram".localized)
                        .fontWeight(.medium)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.enlikoCard)
                .foregroundColor(.enlikoPrimary)
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.enlikoPrimary.opacity(0.5), lineWidth: 1)
                )
            }
            
            Text("auth_expires_in_5_min".localized)
                .font(.caption)
                .foregroundColor(.enlikoTextMuted)
        }
        .enlikoCard()
        .padding(20)
    }
    
    // MARK: - Link Email Section (after TG login)
    private var linkEmailSection: some View {
        VStack(spacing: 24) {
            VStack(spacing: 8) {
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 50))
                    .foregroundColor(.green)
                
                Text("auth_logged_in_success".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                
                Text("auth_add_email_prompt".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                    .multilineTextAlignment(.center)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                EnlikoTextField(icon: "envelope", placeholder: "auth_email_placeholder".localized, text: $email)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .onChange(of: email) { _, _ in validateEmail() }
                
                if !emailError.isEmpty {
                    Text(emailError)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.horizontal, 4)
                }
            }
            
            Button(action: linkEmailToAccount) {
                HStack {
                    if authManager.isLoading {
                        ProgressView().tint(.white)
                    } else {
                        Text("auth_link_email_button".localized)
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 54)
                .background(isEmailValid ? Color.enlikoGradient : LinearGradient(colors: [.gray.opacity(0.4), .gray.opacity(0.3)], startPoint: .leading, endPoint: .trailing))
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(!isEmailValid || authManager.isLoading)
            
            Button(action: skipLinkEmail) {
                Text("auth_skip_for_now".localized)
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextMuted)
            }
        }
        .enlikoCard()
        .padding(20)
    }
    
    // MARK: - Verification Section
    private var verificationSection: some View {
        VStack(spacing: 24) {
            HStack {
                Button(action: { showVerification = false }) {
                    Image(systemName: "chevron.left")
                        .font(.title3)
                        .foregroundColor(.enlikoPrimary)
                }
                Spacer()
                Text("auth_verify_email_title".localized)
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Image(systemName: "chevron.left")
                    .font(.title3)
                    .opacity(0)
            }
            
            VStack(spacing: 8) {
                Image(systemName: "envelope.badge.fill")
                    .font(.system(size: 50))
                    .foregroundColor(.enlikoPrimary)
                
                Text("auth_code_sent_to".localized + " \(email)")
                    .font(.subheadline)
                    .foregroundColor(.enlikoTextSecondary)
                    .multilineTextAlignment(.center)
            }
            
            TextField("000000", text: $verificationCode)
                .keyboardType(.numberPad)
                .textContentType(.oneTimeCode)
                .font(.title.monospaced())
                .multilineTextAlignment(.center)
                .padding()
                .background(Color.enlikoSurface)
                .cornerRadius(10)
                .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.enlikoCardHover, lineWidth: 1))
            
            Button(action: verifyEmail) {
                HStack {
                    if authManager.isLoading {
                        ProgressView().tint(.white)
                    } else {
                        Text("auth_verify".localized).fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(Color.enlikoGradient)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(verificationCode.count < 4)
            
            Button("common_back".localized) { showVerification = false }
                .foregroundColor(.enlikoTextSecondary)
        }
        .enlikoCard()
        .padding(20)
    }
    
    // MARK: - Demo Section
    private var demoSection: some View {
        VStack(spacing: 12) {
            Divider().background(Color.enlikoTextMuted)
            Text("debug_dev_mode".localized)
                .font(.caption)
                .foregroundColor(.enlikoTextMuted)
            
            Button(action: { showDemoAlert = true }) {
                HStack {
                    Image(systemName: "play.circle.fill")
                    Text("debug_demo_login".localized)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(Color.enlikoCard)
                .foregroundColor(.enlikoPrimary)
                .cornerRadius(10)
                .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.enlikoPrimary.opacity(0.5), lineWidth: 1))
            }
        }
    }
    
    // MARK: - 2FA Actions
    private var isUsernameValid: Bool {
        let cleaned = telegramUsername.trimmingCharacters(in: .whitespaces).lowercased()
        return cleaned.count >= 3 && cleaned.count <= 32
    }
    
    private func request2FALogin() {
        Task {
            authManager.isLoading = true
            twoFAError = ""
            
            let cleaned = telegramUsername.trimmingCharacters(in: .whitespaces).lowercased().replacingOccurrences(of: "@", with: "")
            
            do {
                let result: Request2FAResponse = try await NetworkService.shared.post(
                    "/auth/telegram/request-2fa",
                    body: ["username": cleaned]
                )
                
                if result.success, let reqId = result.request_id {
                    requestId = reqId
                    isWaitingFor2FA = true
                    startPolling()
                } else {
                    twoFAError = result.message ?? "auth_unknown_error".localized
                }
            } catch let error as NetworkError {
                switch error {
                case .serverError(_, let detail):
                    twoFAError = detail ?? "auth_unknown_error".localized
                default:
                    twoFAError = error.localizedDescription
                }
            } catch {
                twoFAError = error.localizedDescription
            }
            
            authManager.isLoading = false
        }
    }
    
    private func startPolling() {
        stopPolling()
        
        pollingTimer = Timer.scheduledTimer(withTimeInterval: 2.5, repeats: true) { _ in
            Task {
                await check2FAStatus()
            }
        }
    }
    
    private func stopPolling() {
        pollingTimer?.invalidate()
        pollingTimer = nil
    }
    
    private func check2FAStatus() async {
        guard let reqId = requestId else { return }
        
        do {
            let result: Check2FAResponse = try await NetworkService.shared.get(
                "/auth/telegram/check-2fa/\(reqId)"
            )
            
            switch result.status {
            case "approved":
                stopPolling()
                if let token = result.token, let user = result.user {
                    await MainActor.run {
                        // Check if user has email - if not, prompt to add
                        if user.email == nil || user.email?.isEmpty == true {
                            showLinkEmail = true
                            isWaitingFor2FA = false
                        }
                        authManager.handleSuccessfulLogin(token: token, refreshToken: result.refresh_token, user: user)
                    }
                }
                
            case "rejected":
                stopPolling()
                await MainActor.run {
                    twoFAError = "auth_login_rejected".localized
                    isWaitingFor2FA = false
                }
                
            case "expired":
                stopPolling()
                await MainActor.run {
                    twoFAError = "auth_request_expired".localized
                    isWaitingFor2FA = false
                }
                
            case "pending":
                break
                
            default:
                break
            }
        } catch {
            print("Polling error: \(error)")
        }
    }
    
    private func openTelegramApp() {
        if let url = URL(string: "tg://") {
            if UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url)
            }
        }
    }
    
    // MARK: - Email Actions
    private func submitEmailForm() {
        Task {
            if isRegistering {
                // Clean up telegram username (remove @ if present)
                var tgUsername: String? = nil
                if !telegramUsernameReg.isEmpty {
                    tgUsername = telegramUsernameReg.hasPrefix("@") 
                        ? String(telegramUsernameReg.dropFirst()) 
                        : telegramUsernameReg
                }
                
                let success = await authManager.registerWithEmail(
                    email: email, password: password,
                    firstName: firstName.isEmpty ? nil : firstName,
                    lastName: lastName.isEmpty ? nil : lastName,
                    telegramUsername: tgUsername
                )
                if success { showVerification = true }
            } else {
                _ = await authManager.loginWithEmail(email: email, password: password)
            }
        }
    }
    
    private func verifyEmail() {
        Task { await authManager.verifyEmail(email: email, code: verificationCode) }
    }
    
    private func linkEmailToAccount() {
        Task {
            // TODO: Implement link email API call
            // For now, skip after success
            showLinkEmail = false
        }
    }
    
    private func skipLinkEmail() {
        showLinkEmail = false
    }
    
    // MARK: - Validation
    private var isFormValid: Bool {
        guard !email.isEmpty, !password.isEmpty, isEmailValid else { return false }
        return isRegistering ? isPasswordValid : true
    }
    
    private var isEmailValid: Bool {
        let regex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        return NSPredicate(format: "SELF MATCHES %@", regex).evaluate(with: email)
    }
    
    private var isPasswordValid: Bool {
        password.count >= 8 && password.contains(where: { $0.isLetter }) && password.contains(where: { $0.isNumber })
    }
    
    private func validateEmail() {
        emailError = email.isEmpty ? "" : (isEmailValid ? "" : "error_invalid_email".localized)
    }
    
    private func validatePassword() {
        guard isRegistering else { passwordError = ""; return }
        if password.isEmpty { passwordError = "" }
        else if password.count < 8 { passwordError = "auth_password_too_short".localized }
        else if !password.contains(where: { $0.isLetter }) { passwordError = "auth_password_needs_letters".localized }
        else if !password.contains(where: { $0.isNumber }) { passwordError = "auth_password_needs_numbers".localized }
        else { passwordError = "" }
    }
}

// MARK: - Response Models
struct Request2FAResponse: Codable {
    let success: Bool
    let request_id: String?
    let message: String?
}

struct Check2FAResponse: Codable {
    let status: String
    let message: String?
    let token: String?
    let refresh_token: String?
    let user: User?
}

// MARK: - Custom Text Fields
struct EnlikoTextField: View {
    let icon: String
    let placeholder: String
    @Binding var text: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon).foregroundColor(.enlikoTextSecondary).frame(width: 20)
            TextField(placeholder, text: $text).foregroundColor(.white)
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(10)
        .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.enlikoCardHover, lineWidth: 1))
    }
}

struct EnlikoSecureField: View {
    let icon: String
    let placeholder: String
    @Binding var text: String
    @State private var isSecure = true
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon).foregroundColor(.enlikoTextSecondary).frame(width: 20)
            if isSecure {
                SecureField(placeholder, text: $text).foregroundColor(.white)
            } else {
                TextField(placeholder, text: $text).foregroundColor(.white)
            }
            Button(action: { isSecure.toggle() }) {
                Image(systemName: isSecure ? "eye.slash" : "eye").foregroundColor(.enlikoTextSecondary)
            }
        }
        .padding()
        .background(Color.enlikoSurface)
        .cornerRadius(10)
        .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.enlikoCardHover, lineWidth: 1))
    }
}

#Preview {
    LoginView()
        .environmentObject(AuthManager.shared)
        .preferredColorScheme(.dark)
}
