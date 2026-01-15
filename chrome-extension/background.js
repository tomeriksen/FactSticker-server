/**
 * FactSticker Chrome Extension - Background Service Worker
 *
 * When the user clicks the extension icon, this script:
 * 1. Injects a content script to extract article text from the page
 * 2. Stores the content in chrome.storage.local
 * 3. Opens the FactSticker quiz in a new tab (which reads from storage)
 */

// Server URL - change this if running on a different host/port
const FACTSTICKER_SERVER = 'http://127.0.0.1:5001';

// Listen for messages from the quiz page requesting article content
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
    if (message.type === 'GET_ARTICLE') {
        chrome.storage.local.get('factsticker_article', (result) => {
            const article = result.factsticker_article || {};
            console.log('Sending article to quiz page:', article.content?.substring(0, 100));
            sendResponse(article);
        });
        return true; // Keep the message channel open for async response
    }
});

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

        console.log('Extracted content length:', articleContent.length);

        // Store content in chrome.storage.local for the quiz page to retrieve
        await chrome.storage.local.set({
            factsticker_article: {
                url: articleUrl,
                content: articleContent,
                title: articleTitle,
                timestamp: Date.now()
            }
        });

        // Open the quiz page
        chrome.tabs.create({
            url: `${FACTSTICKER_SERVER}/quiz?url=${encodeURIComponent(articleUrl)}&ext=1`
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
