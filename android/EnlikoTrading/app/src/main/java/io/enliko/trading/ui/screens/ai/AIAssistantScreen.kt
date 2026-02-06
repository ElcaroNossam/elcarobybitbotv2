package io.enliko.trading.ui.screens.ai

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import io.enliko.trading.ui.theme.LongGreen
import io.enliko.trading.ui.theme.ShortRed
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// MARK: - Data Models
data class ChatMessage(
    val id: String,
    val content: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val isTyping: Boolean = false,
    val suggestions: List<String> = emptyList(),
    val tradeSignal: TradeSignal? = null
)

data class TradeSignal(
    val symbol: String,
    val side: String,
    val confidence: Int,
    val entryPrice: Double,
    val takeProfit: Double,
    val stopLoss: Double,
    val reason: String
)

data class QuickAction(
    val id: String,
    val label: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
    val prompt: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AIAssistantScreen(
    onNavigateBack: () -> Unit = {},
    onExecuteTrade: (TradeSignal) -> Unit = {}
) {
    var messages by remember { mutableStateOf(listOf<ChatMessage>()) }
    var inputText by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    
    val quickActions = remember {
        listOf(
            QuickAction("market", "Market Analysis", Icons.Filled.Analytics, "Analyze the current crypto market"),
            QuickAction("btc", "BTC Analysis", Icons.Filled.CurrencyBitcoin, "What's your analysis on Bitcoin?"),
            QuickAction("signals", "Trading Signals", Icons.Filled.TrendingUp, "Any good trading signals right now?"),
            QuickAction("portfolio", "Portfolio Review", Icons.Filled.AccountBalance, "Review my portfolio performance"),
            QuickAction("news", "Crypto News", Icons.Filled.Newspaper, "What's the latest crypto news?"),
            QuickAction("strategy", "Strategy Tips", Icons.Filled.Lightbulb, "Give me some trading strategy tips")
        )
    }
    
    // Initial greeting
    LaunchedEffect(Unit) {
        messages = listOf(
            ChatMessage(
                id = "welcome",
                content = "👋 Hello! I'm your AI Trading Assistant.\n\nI can help you with:\n• Market analysis\n• Trading signals\n• Portfolio insights\n• Strategy recommendations\n\nHow can I assist you today?",
                isUser = false,
                suggestions = listOf(
                    "Analyze BTC/USDT",
                    "Best trades today?",
                    "Market sentiment"
                )
            )
        )
    }
    
    // Auto-scroll on new message
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.lastIndex)
        }
    }
    
    fun sendMessage(text: String) {
        if (text.isBlank()) return
        
        // Add user message
        val userMessage = ChatMessage(
            id = "user_${System.currentTimeMillis()}",
            content = text,
            isUser = true
        )
        messages = messages + userMessage
        inputText = ""
        isLoading = true
        
        // Simulate AI response
        scope.launch {
            // Add typing indicator
            val typingMessage = ChatMessage(
                id = "typing",
                content = "",
                isUser = false,
                isTyping = true
            )
            messages = messages + typingMessage
            
            delay(1500 + (500..1500).random().toLong())
            
            // Generate response based on input
            val response = generateAIResponse(text)
            
            // Remove typing and add response
            messages = messages.filter { it.id != "typing" } + response
            isLoading = false
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(
                                    Brush.linearGradient(
                                        colors = listOf(
                                            Color(0xFF6366F1),
                                            Color(0xFF8B5CF6),
                                            Color(0xFFEC4899)
                                        )
                                    )
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Filled.Psychology,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text("AI Assistant", fontWeight = FontWeight.Bold)
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(LongGreen)
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    "Online",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = LongGreen
                                )
                            }
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { /* Clear chat */ messages = emptyList() }) {
                        Icon(Icons.Default.DeleteSweep, contentDescription = "Clear")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Quick Actions
            if (messages.size <= 1) {
                QuickActionsRow(
                    actions = quickActions,
                    onActionClick = { action -> sendMessage(action.prompt) }
                )
            }
            
            // Chat Messages
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(messages) { message ->
                    ChatBubble(
                        message = message,
                        onSuggestionClick = { sendMessage(it) },
                        onExecuteTrade = onExecuteTrade
                    )
                }
            }
            
            // Input Area
            ChatInput(
                value = inputText,
                onValueChange = { inputText = it },
                onSend = { sendMessage(inputText) },
                isLoading = isLoading
            )
        }
    }
}

@Composable
private fun QuickActionsRow(
    actions: List<QuickAction>,
    onActionClick: (QuickAction) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(actions.chunked(2)) { rowActions ->
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                rowActions.forEach { action ->
                    OutlinedCard(
                        onClick = { onActionClick(action) },
                        modifier = Modifier.weight(1f)
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                action.icon,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                action.label,
                                style = MaterialTheme.typography.bodySmall,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }
                if (rowActions.size < 2) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun ChatBubble(
    message: ChatMessage,
    onSuggestionClick: (String) -> Unit,
    onExecuteTrade: (TradeSignal) -> Unit
) {
    val bubbleColor = if (message.isUser) {
        MaterialTheme.colorScheme.primary
    } else {
        MaterialTheme.colorScheme.surfaceVariant
    }
    
    val textColor = if (message.isUser) {
        MaterialTheme.colorScheme.onPrimary
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (message.isUser) Alignment.End else Alignment.Start
    ) {
        if (message.isTyping) {
            TypingIndicator()
        } else {
            Surface(
                shape = RoundedCornerShape(
                    topStart = 16.dp,
                    topEnd = 16.dp,
                    bottomStart = if (message.isUser) 16.dp else 4.dp,
                    bottomEnd = if (message.isUser) 4.dp else 16.dp
                ),
                color = bubbleColor,
                modifier = Modifier.widthIn(max = 300.dp)
            ) {
                Text(
                    text = message.content,
                    modifier = Modifier.padding(12.dp),
                    color = textColor,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
            
            // Trade Signal Card
            message.tradeSignal?.let { signal ->
                Spacer(modifier = Modifier.height(8.dp))
                TradeSignalCard(signal = signal, onExecute = { onExecuteTrade(signal) })
            }
            
            // Suggestions
            if (message.suggestions.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    message.suggestions.forEach { suggestion ->
                        SuggestionChip(
                            onClick = { onSuggestionClick(suggestion) },
                            label = { Text(suggestion, style = MaterialTheme.typography.labelSmall) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun TypingIndicator() {
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(16.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        repeat(3) { index ->
            var alpha by remember { mutableFloatStateOf(0.3f) }
            
            LaunchedEffect(Unit) {
                while (true) {
                    delay(index * 200L)
                    alpha = 1f
                    delay(300)
                    alpha = 0.3f
                    delay(600)
                }
            }
            
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = alpha))
            )
        }
    }
}

@Composable
private fun TradeSignalCard(
    signal: TradeSignal,
    onExecute: () -> Unit
) {
    val sideColor = if (signal.side == "LONG") LongGreen else ShortRed
    
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = sideColor.copy(alpha = 0.1f)
        ),
        modifier = Modifier.widthIn(max = 300.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "${signal.symbol} ${signal.side}",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = sideColor
                )
                Surface(
                    shape = RoundedCornerShape(4.dp),
                    color = sideColor
                ) {
                    Text(
                        text = "${signal.confidence}% confidence",
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("Entry", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("$${String.format("%.2f", signal.entryPrice)}", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
                }
                Column {
                    Text("TP", style = MaterialTheme.typography.labelSmall, color = LongGreen)
                    Text("$${String.format("%.2f", signal.takeProfit)}", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = LongGreen)
                }
                Column {
                    Text("SL", style = MaterialTheme.typography.labelSmall, color = ShortRed)
                    Text("$${String.format("%.2f", signal.stopLoss)}", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = ShortRed)
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = signal.reason,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Button(
                onClick = onExecute,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = sideColor),
                shape = RoundedCornerShape(8.dp)
            ) {
                Icon(Icons.Default.FlashOn, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("Execute Trade")
            }
        }
    }
}

@Composable
private fun ChatInput(
    value: String,
    onValueChange: (String) -> Unit,
    onSend: () -> Unit,
    isLoading: Boolean
) {
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shadowElevation = 8.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            OutlinedTextField(
                value = value,
                onValueChange = onValueChange,
                modifier = Modifier.weight(1f),
                placeholder = { Text("Ask me anything about trading...") },
                enabled = !isLoading,
                shape = RoundedCornerShape(24.dp),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                keyboardActions = KeyboardActions(onSend = { onSend() }),
                maxLines = 3
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            FilledIconButton(
                onClick = onSend,
                enabled = value.isNotBlank() && !isLoading,
                shape = CircleShape
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        strokeWidth = 2.dp
                    )
                } else {
                    Icon(Icons.Default.Send, contentDescription = "Send")
                }
            }
        }
    }
}

private fun generateAIResponse(input: String): ChatMessage {
    val lowerInput = input.lowercase()
    
    // Generate contextual responses
    return when {
        lowerInput.contains("btc") || lowerInput.contains("bitcoin") -> {
            ChatMessage(
                id = "ai_${System.currentTimeMillis()}",
                content = "📊 **BTC/USDT Analysis**\n\nCurrent Price: \$98,450\n24h Change: +2.3%\n\n**Technical Outlook:**\n• RSI (14): 62 - Neutral\n• MACD: Bullish crossover\n• Support: \$96,500\n• Resistance: \$100,000\n\n**Sentiment:** Bullish 🟢\n\nBitcoin is showing strong momentum with accumulation patterns visible on the 4H chart.",
                isUser = false,
                suggestions = listOf("Trade BTC", "Set alert", "More coins"),
                tradeSignal = TradeSignal(
                    symbol = "BTCUSDT",
                    side = "LONG",
                    confidence = 75,
                    entryPrice = 98450.0,
                    takeProfit = 102000.0,
                    stopLoss = 96000.0,
                    reason = "Bullish breakout pattern with strong volume"
                )
            )
        }
        lowerInput.contains("signal") || lowerInput.contains("trade") -> {
            ChatMessage(
                id = "ai_${System.currentTimeMillis()}",
                content = "🎯 **Top Trading Signals**\n\nI've identified 3 high-probability setups:\n\n1. **ETH/USDT** - Long\n   Confidence: 78%\n   Entry: \$3,450\n\n2. **SOL/USDT** - Long  \n   Confidence: 72%\n   Entry: \$185\n\n3. **XRP/USDT** - Short\n   Confidence: 65%\n   Entry: \$0.52\n\nWould you like detailed analysis on any of these?",
                isUser = false,
                suggestions = listOf("ETH details", "Execute all", "Risk settings"),
                tradeSignal = TradeSignal(
                    symbol = "ETHUSDT",
                    side = "LONG",
                    confidence = 78,
                    entryPrice = 3450.0,
                    takeProfit = 3720.0,
                    stopLoss = 3280.0,
                    reason = "Double bottom pattern confirmed"
                )
            )
        }
        lowerInput.contains("market") || lowerInput.contains("sentiment") -> {
            ChatMessage(
                id = "ai_${System.currentTimeMillis()}",
                content = "🌍 **Market Overview**\n\n**Global Sentiment:** Greed (68/100)\n\n**Key Metrics:**\n• Total Market Cap: \$3.45T (+1.8%)\n• BTC Dominance: 52.3%\n• 24h Volume: \$125B\n• Altcoin Season Index: 42/100\n\n**Notable Movers:**\n🟢 SOL +8.5%\n🟢 AVAX +6.2%\n🔴 DOGE -3.1%\n\n**My Take:** Market is bullish with moderate risk appetite. Focus on large caps.",
                isUser = false,
                suggestions = listOf("Top gainers", "Fear & Greed", "DeFi analysis")
            )
        }
        lowerInput.contains("portfolio") || lowerInput.contains("performance") -> {
            ChatMessage(
                id = "ai_${System.currentTimeMillis()}",
                content = "📈 **Portfolio Analysis**\n\n**30-Day Performance:**\n• Total PnL: +\$1,245.80 (+12.4%)\n• Win Rate: 68%\n• Avg Trade: +2.1%\n• Max Drawdown: -8.3%\n\n**Recommendations:**\n1. Consider taking partial profits on ETH\n2. BTC position is healthy, hold\n3. Reduce exposure to meme coins\n\n**Risk Score:** 6.5/10 (Moderate)",
                isUser = false,
                suggestions = listOf("Rebalance", "Risk report", "Compare to BTC")
            )
        }
        lowerInput.contains("strategy") || lowerInput.contains("tip") -> {
            ChatMessage(
                id = "ai_${System.currentTimeMillis()}",
                content = "💡 **Trading Strategy Tips**\n\n**For Current Market:**\n\n1. **Scale Into Positions**\n   Use 25% entries rather than full size\n\n2. **Use Trailing Stops**\n   Lock in profits as price moves\n\n3. **Watch Correlation**\n   BTC leads - wait for confirmation\n\n4. **Risk Management**\n   Never risk >2% per trade\n   Keep 30% in stablecoins\n\n5. **Best Timeframes**\n   4H for trends, 15m for entries",
                isUser = false,
                suggestions = listOf("Setup alerts", "Backtest strategy", "More tips")
            )
        }
        else -> {
            ChatMessage(
                id = "ai_${System.currentTimeMillis()}",
                content = "I understand you're asking about \"$input\".\n\nI can help you with:\n• Technical analysis\n• Trading signals\n• Portfolio management\n• Market insights\n• Strategy recommendations\n\nCould you be more specific about what you'd like to know?",
                isUser = false,
                suggestions = listOf("BTC analysis", "Trade signals", "My portfolio")
            )
        }
    }
}
