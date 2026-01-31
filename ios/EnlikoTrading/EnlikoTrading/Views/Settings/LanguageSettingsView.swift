//
//  LanguageSettingsView.swift
//  EnlikoTrading
//
//  Language selection view with 15 supported languages
//

import SwiftUI

struct LanguageSettingsView: View {
    @ObservedObject var localization = LocalizationManager.shared
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Color.enlikoBackground.ignoresSafeArea()
            
            List {
                ForEach(AppLanguage.allCases) { language in
                    LanguageRow(
                        language: language,
                        isSelected: localization.currentLanguage == language
                    ) {
                        localization.setLanguage(language)
                        
                        // Dismiss after short delay to show selection
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                            dismiss()
                        }
                    }
                }
                .listRowBackground(Color.enlikoCard)
            }
            .listStyle(.insetGrouped)
            .scrollContentBackground(.hidden)
        }
        .navigationTitle("settings_language".localized)
        .navigationBarTitleDisplayMode(.inline)
        .withRTLSupport()
    }
}

// MARK: - Language Row
struct LanguageRow: View {
    let language: AppLanguage
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                // Flag
                Text(language.flag)
                    .font(.title2)
                
                // Language name
                VStack(alignment: .leading, spacing: 2) {
                    Text(language.displayName)
                        .font(.body)
                        .foregroundColor(.white)
                    
                    Text(language.rawValue.uppercased())
                        .font(.caption)
                        .foregroundColor(.enlikoTextSecondary)
                }
                
                Spacer()
                
                // Checkmark
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title3)
                        .foregroundColor(.enlikoPrimary)
                }
            }
            .padding(.vertical, 8)
        }
    }
}

// MARK: - Compact Language Picker (for inline use)
struct CompactLanguagePicker: View {
    @ObservedObject var localization = LocalizationManager.shared
    @State private var showPicker = false
    
    var body: some View {
        Button(action: { showPicker = true }) {
            HStack(spacing: 8) {
                Text(localization.currentLanguage.flag)
                    .font(.title3)
                
                Text(localization.currentLanguage.rawValue.uppercased())
                    .font(.caption.weight(.medium))
                    .foregroundColor(.enlikoTextSecondary)
                
                Image(systemName: "chevron.down")
                    .font(.caption2)
                    .foregroundColor(.enlikoTextMuted)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color.enlikoCard)
            .cornerRadius(8)
        }
        .sheet(isPresented: $showPicker) {
            NavigationStack {
                LanguageSettingsView()
                    .navigationBarItems(trailing: Button("common_close".localized) {
                        showPicker = false
                    })
            }
            .presentationDetents([.medium, .large])
        }
    }
}

// MARK: - Language Grid (for onboarding)
struct LanguageGrid: View {
    @ObservedObject var localization = LocalizationManager.shared
    let onSelect: (AppLanguage) -> Void
    
    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible()),
        GridItem(.flexible())
    ]
    
    var body: some View {
        LazyVGrid(columns: columns, spacing: 12) {
            ForEach(AppLanguage.allCases) { language in
                LanguageGridItem(
                    language: language,
                    isSelected: localization.currentLanguage == language
                ) {
                    localization.setLanguage(language)
                    onSelect(language)
                }
            }
        }
    }
}

struct LanguageGridItem: View {
    let language: AppLanguage
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Text(language.flag)
                    .font(.largeTitle)
                
                Text(language.rawValue.uppercased())
                    .font(.caption.weight(.medium))
                    .foregroundColor(isSelected ? .enlikoPrimary : .enlikoTextSecondary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? Color.enlikoPrimary.opacity(0.15) : Color.enlikoCard)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isSelected ? Color.enlikoPrimary : Color.clear, lineWidth: 2)
            )
        }
    }
}

#Preview {
    NavigationStack {
        LanguageSettingsView()
    }
    .preferredColorScheme(.dark)
}
