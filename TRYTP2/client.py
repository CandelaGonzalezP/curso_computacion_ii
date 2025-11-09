#!/usr/bin/env python3
"""
Cliente de prueba para el sistema de scraping
"""

import argparse
import asyncio
import aiohttp
import json
import sys
from typing import Optional


async def test_scraping(host: str, port: int, url: str, use_post: bool = False):
    """
    Probar endpoint de scraping
    
    Args:
        host: Host del servidor
        port: Puerto del servidor
        url: URL a scrapear
        use_post: Usar POST en lugar de GET
    """
    server_url = f"http://{host}:{port}/scrape"
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"🔍 Scraping: {url}")
            print(f"📡 Server: {server_url}")
            print(f"🔧 Method: {'POST' if use_post else 'GET'}")
            print("-" * 60)
            
            if use_post:
                # POST request
                async with session.post(
                    server_url,
                    json={'url': url},
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as response:
                    result = await response.json()
            else:
                # GET request
                async with session.get(
                    server_url,
                    params={'url': url},
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as response:
                    result = await response.json()
            
            # Mostrar resultados
            print_results(result)
            
            return result
            
        except asyncio.TimeoutError:
            print("❌ Error: Request timeout")
            return None
        except aiohttp.ClientError as e:
            print(f"❌ Client Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return None


def print_results(result: dict):
    """Imprimir resultados de forma legible"""
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    # Status
    status = result.get('status', 'unknown')
    status_emoji = "✅" if status == 'success' else "⚠️"
    print(f"\n{status_emoji} Status: {status}")
    
    # URL y timestamp
    print(f"🔗 URL: {result.get('url', 'N/A')}")
    print(f"🕐 Timestamp: {result.get('timestamp', 'N/A')}")
    
    # Scraping Data
    scraping_data = result.get('scraping_data', {})
    if scraping_data and not scraping_data.get('error'):
        print("\n" + "-"*60)
        print("📝 SCRAPING DATA")
        print("-"*60)
        
        print(f"📌 Title: {scraping_data.get('title', 'N/A')}")
        print(f"🔗 Links Found: {len(scraping_data.get('links', []))}")
        print(f"🖼️  Images Count: {scraping_data.get('images_count', 0)}")
        
        # Structure
        structure = scraping_data.get('structure', {})
        if structure:
            print("\n📋 Page Structure:")
            for tag, count in sorted(structure.items()):
                if count > 0:
                    print(f"   {tag.upper()}: {count}")
        
        # Meta tags
        meta_tags = scraping_data.get('meta_tags', {})
        if meta_tags:
            print("\n🏷️  Meta Tags:")
            for key, value in list(meta_tags.items())[:5]:  # Primeros 5
                value_short = value[:60] + "..." if len(value) > 60 else value
                print(f"   {key}: {value_short}")
            if len(meta_tags) > 5:
                print(f"   ... and {len(meta_tags) - 5} more")
        
        # Links (primeros 5)
        links = scraping_data.get('links', [])
        if links:
            print(f"\n🔗 Sample Links ({min(5, len(links))} of {len(links)}):")
            for link in links[:5]:
                link_short = link[:70] + "..." if len(link) > 70 else link
                print(f"   • {link_short}")
    
    # Processing Data
    processing_data = result.get('processing_data', {})
    if processing_data:
        print("\n" + "-"*60)
        print("⚙️  PROCESSING DATA")
        print("-"*60)
        
        if processing_data.get('error'):
            print(f"⚠️  Error: {processing_data['error']}")
        else:
            # Performance
            performance = processing_data.get('performance', {})
            if performance and not performance.get('error'):
                print("\n📊 Performance Metrics:")
                print(f"   ⏱️  Load Time: {performance.get('load_time_ms', 0)} ms")
                print(f"   💾 Total Size: {performance.get('total_size_kb', 0)} KB")
                print(f"   📦 Requests: {performance.get('num_requests', 0)}")
                
                breakdown = performance.get('breakdown', {})
                if breakdown:
                    print(f"\n   Breakdown:")
                    print(f"      HTML: {breakdown.get('html_size_kb', 0)} KB")
                    print(f"      Scripts: {breakdown.get('scripts', 0)}")
                    print(f"      Stylesheets: {breakdown.get('stylesheets', 0)}")
                    print(f"      Images: {breakdown.get('images', 0)}")
            
            # Screenshot
            screenshot = processing_data.get('screenshot')
            if screenshot:
                size_kb = len(screenshot) / 1024
                print(f"\n📸 Screenshot: {size_kb:.1f} KB (base64 encoded)")
            elif screenshot is None:
                print("\n📸 Screenshot: Not available")
            
            # Thumbnails
            thumbnails = processing_data.get('thumbnails', [])
            if thumbnails:
                total_size = sum(len(t) for t in thumbnails) / 1024
                print(f"\n🖼️  Thumbnails: {len(thumbnails)} generated ({total_size:.1f} KB total)")
    
    print("\n" + "="*60 + "\n")


async def test_health(host: str, port: int):
    """Probar endpoint de health check"""
    server_url = f"http://{host}:{port}/health"
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"🏥 Health Check: {server_url}")
            
            async with session.get(server_url, timeout=5) as response:
                result = await response.json()
                
                if result.get('status') == 'healthy':
                    print("✅ Server is healthy")
                    print(f"   Workers: {result.get('workers')}")
                    print(f"   Timestamp: {result.get('timestamp')}")
                else:
                    print("⚠️  Server status unknown")
                
                return result
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return None


async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Cliente de prueba para sistema de scraping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s --url https://example.com
  %(prog)s --url https://python.org --host localhost --port 8000
  %(prog)s --url https://github.com --post
  %(prog)s --health
        """
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host del servidor (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Puerto del servidor (default: 8000)'
    )
    
    parser.add_argument(
        '--url',
        help='URL a scrapear'
    )
    
    parser.add_argument(
        '--post',
        action='store_true',
        help='Usar POST en lugar de GET'
    )
    
    parser.add_argument(
        '--health',
        action='store_true',
        help='Realizar health check'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Imprimir resultado en formato JSON'
    )
    
    args = parser.parse_args()
    
    # Health check
    if args.health:
        await test_health(args.host, args.port)
        return 0
    
    # Scraping
    if not args.url:
        parser.error("--url is required (unless using --health)")
        return 1
    
    result = await test_scraping(args.host, args.port, args.url, args.post)
    
    if result and args.json:
        print("\n" + "="*60)
        print("JSON OUTPUT")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return 0 if result else 1


if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)