import tkinter as tk
from tkinter import scrolledtext
import threading
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def fetch_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except:
        return None

def extract_links(html, base_url, domain):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == domain:
            links.add(full_url)
    return links

def has_parameters(url):
    return bool(urlparse(url).query)

def crawl(start_url):
    domain = urlparse(start_url).netloc
    visited = set()
    to_visit = [start_url]
    parameterized_urls = set()

    # Add start_url if it has parameters
    if has_parameters(start_url):
        parameterized_urls.add(start_url)

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        html = fetch_page(url)
        if not html:
            continue
        links = extract_links(html, url, domain)
        for link in links:
            if has_parameters(link):
                parameterized_urls.add(link)
            if link not in visited:
                to_visit.append(link)
    return parameterized_urls

def start_crawl():
    start_url = url_entry.get()
    if not start_url.startswith("http"):
        output_text.insert(tk.END, "❌ Please enter a valid URL starting with http or https\n")
        return
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"🔍 Crawling: {start_url}\n\n")
    results = crawl(start_url)

    if results:
        for url in results:
            output_text.insert(tk.END, url + "\n")

        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "parameterized_urls.csv")
            with open(desktop_path, "w") as file:
                for url in results:
                    file.write(url + "\n")
            output_text.insert(tk.END, f"\n✅ Saved results to: {desktop_path}\n")
        except Exception as e:
            output_text.insert(tk.END, f"\n❌ Error saving file: {e}\n")
    else:
        output_text.insert(tk.END, "⚠️ No parameterized URLs found.\n")

def start_crawl_thread():
    thread = threading.Thread(target=start_crawl)
    thread.start()

# GUI setup
window = tk.Tk()
window.title("Web Crawler for Parameterized URLs")
window.geometry("700x500")

tk.Label(window, text="Enter Website URL:").pack(pady=5)
url_entry = tk.Entry(window, width=80)
url_entry.pack(pady=5)
url_entry.insert(0, "https://httpbin.org/get?param=value")  # Default URL with parameters for testing

tk.Button(window, text="Start Crawl", command=start_crawl_thread).pack(pady=10)

output_text = scrolledtext.ScrolledText(window, width=80, height=20)
output_text.pack(pady=10)

window.mainloop()
