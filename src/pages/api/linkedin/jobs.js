import axios from 'axios';

export default async function handler(req, res) {
  const { keywords, location } = req.query;
  
  try {
    const response = await axios.get('https://api.linkedin.com/v2/jobs', {
      headers: {
        'Authorization': `Bearer ${process.env.LINKEDIN_ACCESS_TOKEN}`,
      },
      params: {
        keywords,
        location,
      }
    });
    
    res.status(200).json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching LinkedIn jobs' });
  }
}