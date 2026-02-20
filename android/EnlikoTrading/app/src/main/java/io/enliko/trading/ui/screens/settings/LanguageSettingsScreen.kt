package io.enliko.trading.ui.screens.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import io.enliko.trading.ui.theme.*
import io.enliko.trading.util.AppLanguage
import io.enliko.trading.util.LocalStrings
import io.enliko.trading.util.Strings

/**
 * LanguageSettingsScreen - Matching iOS LanguageSettingsView.swift
 * Features: Full language list with flags and selection
 */

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LanguageSettingsScreen(
    currentLanguage: AppLanguage,
    onLanguageSelect: (AppLanguage) -> Unit,
    onBack: () -> Unit,
    strings: Strings = LocalStrings.current
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(strings.language) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = strings.back)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = EnlikoBackground
                )
            )
        },
        containerColor = EnlikoBackground
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(AppLanguage.entries) { language ->
                LanguageRow(
                    language = language,
                    isSelected = currentLanguage == language,
                    onClick = {
                        onLanguageSelect(language)
                    }
                )
            }
        }
    }
}

@Composable
fun LanguageRow(
    language: AppLanguage,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick),
        color = EnlikoCard
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Flag
                Text(
                    text = language.flag,
                    fontSize = 28.sp
                )
                
                // Language name
                Column {
                    Text(
                        text = language.displayName,
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium,
                        color = EnlikoTextPrimary
                    )
                    
                    Text(
                        text = language.code.uppercase(),
                        style = MaterialTheme.typography.bodySmall,
                        color = EnlikoTextSecondary
                    )
                }
            }
            
            // Checkmark
            if (isSelected) {
                Icon(
                    imageVector = Icons.Default.Check,
                    contentDescription = "Selected",
                    tint = EnlikoPrimary,
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}

/**
 * CompactLanguagePicker - Inline language picker (for use in forms)
 */
@Composable
fun CompactLanguagePicker(
    currentLanguage: AppLanguage,
    onLanguageClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onLanguageClick),
        color = EnlikoCard
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = currentLanguage.flag,
                fontSize = 20.sp
            )
            
            Text(
                text = currentLanguage.code.uppercase(),
                style = MaterialTheme.typography.labelMedium,
                color = EnlikoTextSecondary
            )
            
            Icon(
                imageVector = Icons.Default.KeyboardArrowDown,
                contentDescription = null,
                tint = EnlikoTextMuted,
                modifier = Modifier.size(16.dp)
            )
        }
    }
}

/**
 * LanguageGrid - Grid layout for onboarding/selection
 */
@Composable
fun LanguageGrid(
    currentLanguage: AppLanguage,
    onLanguageSelect: (AppLanguage) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(3),
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(AppLanguage.entries) { language ->
            LanguageGridItem(
                language = language,
                isSelected = currentLanguage == language,
                onClick = { onLanguageSelect(language) }
            )
        }
    }
}

@Composable
private fun LanguageGridItem(
    language: AppLanguage,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1f)
            .clip(RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .then(
                if (isSelected) {
                    Modifier.border(2.dp, EnlikoPrimary, RoundedCornerShape(12.dp))
                } else {
                    Modifier
                }
            ),
        color = if (isSelected) EnlikoPrimary.copy(alpha = 0.15f) else EnlikoCard
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = language.flag,
                fontSize = 32.sp
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = language.code.uppercase(),
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Medium,
                color = if (isSelected) EnlikoPrimary else EnlikoTextSecondary
            )
        }
    }
}
