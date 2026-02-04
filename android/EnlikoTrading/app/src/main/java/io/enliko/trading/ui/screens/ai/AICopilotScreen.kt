package io.enliko.trading.ui.screens.ai

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * AICopilotScreen - Matching iOS AICopilotView.swift
 * AI trading assistant with chat interface and suggestions
 */

data class ChatMessage(
    val id: String,
    val content: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val isTyping: Boolean = false
)

data class QuickAction(
    val title: String,
    val icon: String,
    val prompt: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AICopilotScreen(
    onBack: () -> Unit = {},
    showBackButton: Boolean = false
) {
    var inputText by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()
    
    val messages = remember {
        mutableStateListOf(
            ChatMessage(
                id = "welcome",
                content = "👋 Hello! I'm your AI trading assistant. I can help you with:\n\n" +
                    "• Market analysis and trends\n" +
                    "• Strategy recommendations\n" +
                    "• Risk management advice\n" +
                    "• Trade setup evaluation\n\n" +
                    "How can I assist you today?",
                isUser = false
            )
        )
    }
    
    val quickActions = remember {
        listOf(
            QuickAction("Analyze BTC", "📊", "Analyze the current Bitcoin market trend and key levels"),
            QuickAction("Best Setup", "🎯", "What's the best trading setup right now?"),
            QuickAction("Risk Check", "⚠️", "Review my current portfolio risk exposure"),
            QuickAction("Market News", "📰", "What's the latest market news affecting crypto?")
        )
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(
                                    Brush.linearGradient(
                                        colors = listOf(EnlikoPrimary, EnlikoSecondary)
                                    )
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("🤖", style = MaterialTheme.typography.titleSmall)
                        }
                        Column {
                            Text(
                                "AI Copilot",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                "Trading Assistant",
                                style = MaterialTheme.typography.bodySmall,
                                color = EnlikoTextSecondary
                            )
                        }
                    }
                },
                navigationIcon = {
                    if (showBackButton) {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                        }
                    }
                },
                actions = {
                    IconButton(onClick = { /* Clear chat */ }) {
                        Icon(Icons.Default.Refresh, contentDescription = "New chat")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = EnlikoBackground
                )
            )
        },
        containerColor = EnlikoBackground,
        bottomBar = {
            ChatInputBar(
                inputText = inputText,
                onInputChange = { inputText = it },
                onSend = {
                    if (inputText.isNotBlank()) {
                        val userMessage = ChatMessage(
                            id = System.currentTimeMillis().toString(),
                            content = inputText,
                            isUser = true
                        )
                        messages.add(userMessage)
                        val prompt = inputText
                        inputText = ""
                        isLoading = true
                        
                        coroutineScope.launch {
                            listState.animateScrollToItem(messages.size - 1)
                            // Simulate AI response
                            delay(1500)
                            messages.add(
                                ChatMessage(
                                    id = "${System.currentTimeMillis()}_response",
                                    content = generateMockResponse(prompt),
                                    isUser = false
                                )
                            )
                            isLoading = false
                            listState.animateScrollToItem(messages.size - 1)
                        }
                    }
                },
                isLoading = isLoading
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            state = listState,
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Quick Actions (only show when no conversation yet)
            if (messages.size <= 1) {
                item {
                    Text(
                        text = "Quick Actions",
                        style = MaterialTheme.typography.titleSmall,
                        color = EnlikoTextSecondary,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                }
                
                item {
                    Column(
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        quickActions.chunked(2).forEach { row ->
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                row.forEach { action ->
                                    QuickActionCard(
                                        action = action,
                                        onClick = {
                                            val userMessage = ChatMessage(
                                                id = System.currentTimeMillis().toString(),
                                                content = action.prompt,
                                                isUser = true
                                            )
                                            messages.add(userMessage)
                                            isLoading = true
                                            
                                            coroutineScope.launch {
                                                delay(1500)
                                                messages.add(
                                                    ChatMessage(
                                                        id = "${System.currentTimeMillis()}_response",
                                                        content = generateMockResponse(action.prompt),
                                                        isUser = false
                                                    )
                                                )
                                                isLoading = false
                                            }
                                        },
                                        modifier = Modifier.weight(1f)
                                    )
                                }
                            }
                        }
                    }
                }
                
                item {
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
            
            // Messages
            items(messages, key = { it.id }) { message ->
                ChatBubble(message = message)
            }
            
            // Loading indicator
            if (isLoading) {
                item {
                    TypingIndicator()
                }
            }
        }
    }
}

@Composable
private fun QuickActionCard(
    action: QuickAction,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onClick,
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = EnlikoCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(action.icon, style = MaterialTheme.typography.titleMedium)
            Text(
                text = action.title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = EnlikoTextPrimary
            )
        }
    }
}

@Composable
private fun ChatBubble(message: ChatMessage) {
    val bubbleColor = if (message.isUser) EnlikoPrimary else EnlikoCard
    val textColor = if (message.isUser) Color.White else EnlikoTextPrimary
    val alignment = if (message.isUser) Alignment.End else Alignment.Start
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = alignment
    ) {
        Surface(
            color = bubbleColor,
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (message.isUser) 16.dp else 4.dp,
                bottomEnd = if (message.isUser) 4.dp else 16.dp
            ),
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Text(
                text = message.content,
                style = MaterialTheme.typography.bodyMedium,
                color = textColor,
                modifier = Modifier.padding(12.dp)
            )
        }
    }
}

@Composable
private fun TypingIndicator() {
    Row(
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Surface(
            color = EnlikoCard,
            shape = RoundedCornerShape(16.dp)
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                repeat(3) { index ->
                    val delay = index * 100L
                    TypingDot(delay)
                }
            }
        }
    }
}

@Composable
private fun TypingDot(delay: Long) {
    var visible by remember { mutableStateOf(true) }
    
    LaunchedEffect(Unit) {
        while (true) {
            kotlinx.coroutines.delay(delay)
            visible = true
            kotlinx.coroutines.delay(400)
            visible = false
            kotlinx.coroutines.delay(400)
        }
    }
    
    Box(
        modifier = Modifier
            .size(8.dp)
            .clip(CircleShape)
            .background(
                if (visible) EnlikoTextSecondary else EnlikoTextSecondary.copy(alpha = 0.3f)
            )
    )
}

@Composable
private fun ChatInputBar(
    inputText: String,
    onInputChange: (String) -> Unit,
    onSend: () -> Unit,
    isLoading: Boolean
) {
    Surface(
        color = EnlikoCard,
        shadowElevation = 8.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = inputText,
                onValueChange = onInputChange,
                placeholder = { Text("Ask anything about trading...") },
                singleLine = true,
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(24.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = EnlikoPrimary,
                    unfocusedBorderColor = EnlikoBorder,
                    focusedContainerColor = EnlikoSurface,
                    unfocusedContainerColor = EnlikoSurface
                )
            )
            
            IconButton(
                onClick = onSend,
                enabled = inputText.isNotBlank() && !isLoading,
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(
                        if (inputText.isNotBlank() && !isLoading) EnlikoPrimary
                        else EnlikoSurface
                    )
            ) {
                Icon(
                    Icons.AutoMirrored.Filled.Send,
                    contentDescription = "Send",
                    tint = if (inputText.isNotBlank() && !isLoading) Color.White else EnlikoTextSecondary
                )
            }
        }
    }
}

private fun generateMockResponse(prompt: String): String {
    return when {
        prompt.contains("BTC", ignoreCase = true) || prompt.contains("Bitcoin", ignoreCase = true) -> {
            "📊 **Bitcoin Analysis**\n\n" +
                "Current price: \$97,150\n" +
                "24h change: +1.25%\n\n" +
                "**Key Levels:**\n" +
                "• Resistance: \$98,500, \$100,000\n" +
                "• Support: \$95,000, \$92,500\n\n" +
                "**Technical Outlook:**\n" +
                "BTC is showing bullish momentum above the 50-day MA. RSI at 58 indicates room for further upside. Watch for a breakout above \$98,500 for continuation.\n\n" +
                "**Recommendation:** 📈 Bullish bias, consider longs on dips to \$95,000 with SL below \$92,500."
        }
        prompt.contains("setup", ignoreCase = true) || prompt.contains("trade", ignoreCase = true) -> {
            "🎯 **Current Best Setups**\n\n" +
                "1. **ETH Long** (Confidence: 75%)\n" +
                "   Entry: \$3,450-\$3,480\n" +
                "   TP: \$3,650\n" +
                "   SL: \$3,350\n\n" +
                "2. **SOL Short** (Confidence: 65%)\n" +
                "   Entry: \$195-\$197\n" +
                "   TP: \$180\n" +
                "   SL: \$205\n\n" +
                "⚠️ Always use proper risk management. Max 1-2% per trade."
        }
        prompt.contains("risk", ignoreCase = true) || prompt.contains("portfolio", ignoreCase = true) -> {
            "⚠️ **Portfolio Risk Analysis**\n\n" +
                "**Current Exposure:**\n" +
                "• Total margin used: \$2,090\n" +
                "• Average leverage: 10x\n" +
                "• Position count: 3\n\n" +
                "**Risk Score: 6/10** (Moderate)\n\n" +
                "**Recommendations:**\n" +
                "• Consider reducing leverage on ETHUSDT (currently 15x)\n" +
                "• Good diversification across assets\n" +
                "• TP/SL levels are well-set\n\n" +
                "💡 Tip: Keep total exposure below 20% of account for optimal risk."
        }
        prompt.contains("news", ignoreCase = true) || prompt.contains("market", ignoreCase = true) -> {
            "📰 **Market News Summary**\n\n" +
                "• **SEC Update:** Positive signals for spot ETH ETF approval\n" +
                "• **Macro:** Fed maintains rates, bullish for risk assets\n" +
                "• **On-chain:** Bitcoin whale accumulation at 6-month high\n" +
                "• **DeFi:** Total TVL up 5% this week\n\n" +
                "**Market Sentiment:** 📈 Bullish (Fear & Greed: 72)"
        }
        else -> {
            "I understand you're asking about \"$prompt\". \n\n" +
                "Based on current market conditions:\n\n" +
                "• The overall crypto market is showing bullish momentum\n" +
                "• BTC dominance is at 52%, indicating altcoin strength\n" +
                "• Key levels to watch for major pairs are well-defined\n\n" +
                "Would you like me to elaborate on any specific aspect? You can ask about:\n" +
                "• Specific coin analysis\n" +
                "• Trade setups\n" +
                "• Risk management\n" +
                "• Strategy recommendations"
        }
    }
}
