/**
 * FactSticker Chrome Extension - Background Service Worker
 *
 * When the user clicks the extension icon, this script:
 * 1. Injects a content script to extract article text from the page
 * 2. Opens the FactSticker quiz in a new tab
 * 3. Passes both URL and content to the quiz page
 */

// Server URL - change this if running on a different host/port
const FACTSTICKER_SERVER = 'http://127.0.0.1:5001';

// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
    const articleUrl = tab.url;

    // Skip browser internal pages
    if (articleUrl.startsWith('chrome://') || articleUrl.startsWith('chrome-extension://')) {
        console.log('Cannot quiz on browser internal pages');
        return;
    }

    try {
        // Inject script to extract article content from the page
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: extractArticleContent
        });

        const articleContent = results[0]?.result || '';
        const articleTitle = tab.title || '';

        // Store content in session storage (too large for URL params)
        // The quiz page will retrieve it
        const quizTab = await chrome.tabs.create({
            url: `${FACTSTICKER_SERVER}/quiz?url=${encodeURIComponent(articleUrl)}`
        });

        // Send the content to the new tab once it's loaded
        chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo) {
            if (tabId === quizTab.id && changeInfo.status === 'complete') {
                chrome.tabs.sendMessage(tabId, {
                    type: 'ARTICLE_CONTENT',
                    content: articleContent,
                    title: articleTitle,
                    url: articleUrl
                });
                chrome.tabs.onUpdated.removeListener(listener);
            }
        });

    } catch (error) {
        console.error('Error extracting content:', error);
        // Fallback: open quiz without content (server will scrape)
        chrome.tabs.create({
            url: `${FACTSTICKER_SERVER}/quiz?url=${encodeURIComponent(articleUrl)}`
        });
    }
});

/**
 * Content script function - extracts readable text from the page.
 * This runs in the context of the web page.
 */
function extractArticleContent() {
    // Try to find the main article content
    const selectors = [
        'article',
        '[role="main"]',
        'main',
        '.post-content',
        '.article-content',
        '.entry-content',
        '.content',
        '#content'
    ];

    let contentElement = null;
    for (const selector of selectors) {
        contentElement = document.querySelector(selector);
        if (contentElement) break;
    }

    // Fallback to body if no article container found
    if (!contentElement) {
        contentElement = document.body;
    }

    // Extract text, removing scripts, styles, nav, footer, etc.
    const clone = contentElement.cloneNode(true);
    const removeSelectors = ['script', 'style', 'nav', 'footer', 'header', 'aside', '.sidebar', '.comments', '.advertisement'];
    removeSelectors.forEach(sel => {
        clone.querySelectorAll(sel).forEach(el => el.remove());
    });

    // Get clean text
    return clone.innerText.trim();
}
