from http.server import BaseHTTPRequestHandler
import json
import re
import random
import hashlib

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}
            
            url = data.get('url', '')
            
            if not url:
                self._send_error(400, 'URL is required')
                return
            
            # Validate Instagram URL
            if not self._is_valid_instagram_url(url):
                self._send_error(400, 'Invalid Instagram URL. Please use a post URL like https://instagram.com/p/...')
                return
            
            # Analyze the post
            result = self._analyze_post(url)
            
            self._send_response(200, result)
            
        except json.JSONDecodeError:
            self._send_error(400, 'Invalid JSON')
        except Exception as e:
            self._send_error(500, str(e))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _send_response(self, status, data):
        self.send_response(status)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, status, message):
        self._send_response(status, {'error': message})
    
    def _is_valid_instagram_url(self, url):
        patterns = [
            r'instagram\.com/p/[\w-]+',
            r'instagram\.com/reel/[\w-]+',
            r'instagram\.com/tv/[\w-]+',
        ]
        return any(re.search(p, url) for p in patterns)
    
    def _get_post_type(self, url):
        if '/reel/' in url:
            return 'Reel'
        elif '/tv/' in url:
            return 'IGTV'
        else:
            # Simulate carousel vs single based on URL hash
            url_hash = int(hashlib.md5(url.encode()).hexdigest(), 16)
            if url_hash % 3 == 0:
                return 'Carousel'
            return 'Single Image'
    
    def _analyze_post(self, url):
        """
        Analyze an Instagram post.
        Since Instagram blocks most scraping, we simulate realistic metrics
        based on the URL pattern. In production, you'd use:
        - Instagram Basic Display API (for own posts)
        - Third-party services like RapidAPI's Instagram scrapers
        - Apify Instagram actors
        """
        
        # Extract post ID for consistent "randomness"
        post_id = re.search(r'/(?:p|reel|tv)/([\w-]+)', url)
        seed = int(hashlib.md5(post_id.group(1).encode()).hexdigest()[:8], 16) if post_id else random.randint(0, 100000)
        random.seed(seed)
        
        post_type = self._get_post_type(url)
        
        # Generate realistic metrics based on post type
        # Reels typically get higher engagement
        base_engagement = {
            'Reel': random.uniform(3.5, 12.0),
            'Carousel': random.uniform(2.0, 6.0),
            'Single Image': random.uniform(1.5, 4.5),
            'IGTV': random.uniform(1.0, 3.0)
        }
        
        engagement_rate = round(base_engagement.get(post_type, 2.0), 2)
        
        # Estimate metrics (assuming ~10k follower account)
        follower_estimate = random.randint(5000, 50000)
        estimated_likes = int(follower_estimate * engagement_rate / 100 * random.uniform(0.8, 1.2))
        estimated_comments = int(estimated_likes * random.uniform(0.02, 0.08))
        
        # Calculate grade
        grade, grade_desc = self._calculate_grade(engagement_rate, post_type)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(engagement_rate, post_type, grade)
        
        return {
            'url': url,
            'post_type': post_type,
            'engagement_rate': engagement_rate,
            'estimated_likes': estimated_likes,
            'estimated_comments': estimated_comments,
            'grade': grade,
            'grade_description': grade_desc,
            'suggestions': suggestions
        }
    
    def _calculate_grade(self, engagement_rate, post_type):
        # Adjust thresholds based on post type
        thresholds = {
            'Reel': [(8, 'A'), (5, 'B'), (3, 'C'), (1.5, 'D')],
            'Carousel': [(5, 'A'), (3, 'B'), (2, 'C'), (1, 'D')],
            'Single Image': [(4, 'A'), (2.5, 'B'), (1.5, 'C'), (0.8, 'D')],
            'IGTV': [(3, 'A'), (2, 'B'), (1, 'C'), (0.5, 'D')]
        }
        
        descriptions = {
            'A': 'Excellent! This post is performing above average.',
            'B': 'Good performance. Above industry average.',
            'C': 'Average engagement. Room for improvement.',
            'D': 'Below average. Consider the suggestions below.',
            'F': 'Needs work. Review content strategy.'
        }
        
        post_thresholds = thresholds.get(post_type, thresholds['Single Image'])
        
        for threshold, grade in post_thresholds:
            if engagement_rate >= threshold:
                return grade, descriptions[grade]
        
        return 'F', descriptions['F']
    
    def _generate_suggestions(self, engagement_rate, post_type, grade):
        all_suggestions = {
            'timing': [
                'Post during peak hours (11am-1pm or 7pm-9pm) for better reach',
                'Test different posting times to find your audience\'s active hours',
                'Consider your audience\'s timezone when scheduling posts'
            ],
            'content': [
                'Use trending audio for Reels to boost discoverability',
                'Add a strong call-to-action in your caption',
                'Start with a hook in the first 3 seconds for video content',
                'Use carousel posts to increase time spent on your content'
            ],
            'hashtags': [
                'Mix popular and niche hashtags (aim for 20-30 relevant tags)',
                'Create a branded hashtag for community building',
                'Research competitor hashtags for inspiration'
            ],
            'engagement': [
                'Reply to comments within the first hour to boost algorithm favor',
                'Ask a question in your caption to encourage comments',
                'Use interactive stickers in Stories to drive engagement'
            ],
            'format': [
                'Reels currently get 2x more reach than static posts',
                'Carousel posts have higher save rates - great for educational content',
                'Add captions/subtitles to videos for accessibility and engagement'
            ]
        }
        
        suggestions = []
        
        # Always suggest based on post type
        if post_type == 'Single Image':
            suggestions.append(random.choice(all_suggestions['format']))
        
        if grade in ['C', 'D', 'F']:
            suggestions.append(random.choice(all_suggestions['timing']))
            suggestions.append(random.choice(all_suggestions['engagement']))
        
        if grade in ['D', 'F']:
            suggestions.append(random.choice(all_suggestions['hashtags']))
        
        # Add content suggestion
        suggestions.append(random.choice(all_suggestions['content']))
        
        # Ensure we have exactly 3 unique suggestions
        unique_suggestions = list(dict.fromkeys(suggestions))[:3]
        while len(unique_suggestions) < 3:
            for category in all_suggestions.values():
                suggestion = random.choice(category)
                if suggestion not in unique_suggestions:
                    unique_suggestions.append(suggestion)
                    break
        
        return unique_suggestions[:3]
