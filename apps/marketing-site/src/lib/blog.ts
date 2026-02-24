import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { format } from 'date-fns';

// Path to blog posts
const postsDirectory = path.join(process.cwd(), 'src/content/blog');

// Debug log for production troubleshooting
const isProduction = process.env.NODE_ENV === 'production';
if (isProduction) {
  console.log('Blog directory path:', postsDirectory);
  try {
    if (fs.existsSync(postsDirectory)) {
      console.log('Blog directory exists, contents:', fs.readdirSync(postsDirectory));
    } else {
      console.log('Blog directory does not exist');
    }
  } catch (error) {
    console.error('Error checking blog directory:', error);
  }
}

export async function renderBlogMarkdown(content: string): Promise<string> {
  const [{ remark }, { default: html }, { default: remarkGfm }] = await Promise.all([
    import('remark'),
    import('remark-html'),
    import('remark-gfm'),
  ]);

  const contentWithYouTubeEmbeds = processYouTubeLinks(content);

  const processedContent = await remark()
    .use(remarkGfm)
    .use(html, { sanitize: false })
    .process(contentWithYouTubeEmbeds);

  return processedContent.toString();
}

// Function to process YouTube links into embeds
function processYouTubeLinks(content: string): string {
  // Match YouTube links in various formats
  const youtubeRegex = /\[([^\]]+)\]\((https:\/\/(?:www\.)?youtube\.com\/(?:watch\?v=|embed\/)([a-zA-Z0-9_-]+)(?:&[^)]+)?)\)/g;
  
  return content.replace(youtubeRegex, (match, text, url, videoId) => {
    return `
<div class="aspect-video relative my-8">
  <iframe 
    src="https://www.youtube.com/embed/${videoId}" 
    title="${text}" 
    class="absolute top-0 left-0 w-full h-full rounded-lg"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
    allowfullscreen
  ></iframe>
</div>
`;
  });
}

export interface BlogPost {
  id: string;
  title: string;
  date: string;
  formattedDate: string;
  excerpt: string;
  content: string;
  contentHtml?: string;
  slug: string;
  author?: string;
  image?: string;
  tags?: string[];
}

// Create the blog directory if it doesn't exist
export function ensureBlogDirectoryExists() {
  try {
    if (!fs.existsSync(postsDirectory)) {
      fs.mkdirSync(postsDirectory, { recursive: true });
    }
  } catch (error) {
    console.error('Error ensuring blog directory exists:', error);
    // In production, we don't want to fail if we can't create the directory
    if (!isProduction) {
      throw error;
    }
  }
}

// Get all blog posts metadata
export function getAllPosts(): BlogPost[] {
  try {
    ensureBlogDirectoryExists();
    
    // Get file names under /posts
    const fileNames = fs.readdirSync(postsDirectory);
    
    if (fileNames.length === 0) {
      console.warn('No blog post files found in directory:', postsDirectory);
      return [];
    }
    
    const allPostsData = fileNames
      .filter(fileName => fileName.endsWith('.md'))
      .map((fileName) => {
        // Remove ".md" from file name to get id
        const id = fileName.replace(/\.md$/, '');
        const slug = id.toLowerCase().replace(/\s+/g, '-');

        // Read markdown file as string
        const fullPath = path.join(postsDirectory, fileName);
        const fileContents = fs.readFileSync(fullPath, 'utf8');

        // Use gray-matter to parse the post metadata section
        const matterResult = matter(fileContents);
        
        // Format the date if it exists
        let formattedDate = '';
        if (matterResult.data.date) {
          try {
            const date = new Date(matterResult.data.date);
            formattedDate = format(date, 'MMMM d, yyyy');
          } catch (error) {
            console.error(`Error formatting date for ${fileName}:`, error);
            formattedDate = matterResult.data.date;
          }
        }

        // Use excerpt from frontmatter or generate from content
        const excerpt = matterResult.data.excerpt || 
          matterResult.content.trim().split('\n')[0].substring(0, 160) + '...';

        return {
          id,
          slug,
          title: matterResult.data.title || id,
          date: matterResult.data.date || '',
          formattedDate,
          excerpt,
          content: matterResult.content,
          author: matterResult.data.author || 'Encypher Team',
          image: matterResult.data.image || '',
          tags: matterResult.data.tags || [],
        };
      });
      
    // Sort posts by date
    return allPostsData.sort((a, b) => {
      if (a.date < b.date) {
        return 1;
      } else {
        return -1;
      }
    });
  } catch (error) {
    console.error('Error getting all posts:', error);
    return [];
  }
}

// Get a single blog post by slug
export async function getPostBySlug(slug: string): Promise<BlogPost | null> {
  try {
    ensureBlogDirectoryExists();
    
    // Find the file that matches the slug
    const fileNames = fs.readdirSync(postsDirectory);
    const fileName = fileNames.find(file => {
      const id = file.replace(/\.md$/, '');
      const fileSlug = id.toLowerCase().replace(/\s+/g, '-');
      return fileSlug === slug;
    });

    if (!fileName) {
      return null;
    }

    const fullPath = path.join(postsDirectory, fileName);
    const fileContents = fs.readFileSync(fullPath, 'utf8');

    // Use gray-matter to parse the post metadata section
    const matterResult = matter(fileContents);
    
    // Format the date if it exists
    let formattedDate = '';
    if (matterResult.data.date) {
      try {
        const date = new Date(matterResult.data.date);
        formattedDate = format(date, 'MMMM d, yyyy');
      } catch (error) {
        console.error(`Error formatting date for ${fileName}:`, error);
        formattedDate = matterResult.data.date;
      }
    }

    const contentHtml = await renderBlogMarkdown(matterResult.content);

    // Use excerpt from frontmatter or generate from content
    const excerpt = matterResult.data.excerpt || 
      matterResult.content.trim().split('\n')[0].substring(0, 160) + '...';

    // Combine the data with the id and contentHtml
    const id = fileName.replace(/\.md$/, '');
    const postSlug = id.toLowerCase().replace(/\s+/g, '-');
    const post: BlogPost = {
      id,
      slug: postSlug,
      title: matterResult.data.title || id,
      date: matterResult.data.date || '',
      content: matterResult.content,
      contentHtml,
      excerpt,
      formattedDate,
      author: matterResult.data.author || 'Encypher Team',
      image: matterResult.data.image || '',
      tags: matterResult.data.tags || [],
    };

    return post;
  } catch (error) {
    console.error(`Error getting post by slug ${slug}:`, error);
    return null;
  }
}

// Get all blog post slugs for static paths
export function getAllPostSlugs(): { params: { slug: string } }[] {
  try {
    ensureBlogDirectoryExists();
    
    const fileNames = fs.readdirSync(postsDirectory);
    return fileNames
      .filter(fileName => fileName.endsWith('.md'))
      .map((fileName) => {
        const id = fileName.replace(/\.md$/, '');
        const slug = id.toLowerCase().replace(/\s+/g, '-');
        return {
          params: {
            slug,
          },
        };
      });
  } catch (error) {
    console.error('Error getting all post slugs:', error);
    return [];
  }
}

// Get all unique tags from all blog posts
export function getAllTags(): { tag: string; count: number }[] {
  try {
    const posts = getAllPosts();
    const tagCounts: Record<string, number> = {};
    
    // Count occurrences of each tag
    posts.forEach(post => {
      if (post.tags && Array.isArray(post.tags)) {
        post.tags.forEach(tag => {
          tagCounts[tag] = (tagCounts[tag] || 0) + 1;
        });
      }
    });
    
    // Convert to array of objects with tag and count
    const tags = Object.keys(tagCounts).map(tag => ({
      tag,
      count: tagCounts[tag]
    }));
    
    // Sort by count (most popular first)
    return tags.sort((a, b) => b.count - a.count);
  } catch (error) {
    console.error('Error getting all tags:', error);
    return [];
  }
}

// Get all blog posts filtered by tag
export async function getPostsByTag(tag: string): Promise<BlogPost[]> {
  try {
    const allPosts = getAllPosts();
    return allPosts.filter(post => 
      post.tags && 
      Array.isArray(post.tags) && 
      post.tags.some(t => t.toLowerCase() === tag.toLowerCase())
    );
  } catch (error) {
    console.error(`Error getting posts by tag ${tag}:`, error);
    return [];
  }
}
