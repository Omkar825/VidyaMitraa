import axios from 'axios';

export default async function handler(req, res) {
  const { keywords, location } = req.query;
  
  try {
    const response = await axios.get('https://api.glassdoor.com/v1/jobs', {
      params: {
        partnerId: process.env.GLASSDOOR_PARTNER_ID,
        key: process.env.GLASSDOOR_API_KEY,
        q: keywords,
        l: location,
      }
    });
    
    res.status(200).json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching Glassdoor jobs' });
  }
}