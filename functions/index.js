const functions = require('firebase-functions');
const nodemailer = require('nodemailer');

// Configure your email service
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'justinl5872@gmail.com',      // UPDATE: Replace with your actual Gmail
    pass: 'sbryatfuxdttdrpz'  // UPDATE: Replace with your app password
  }
});

exports.sendSMS = functions.https.onRequest(async (req, res) => {
  console.log('Function started');
  
  // Enable CORS for all origins//
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    console.log('Handling OPTIONS request');
    res.status(204).send('');
    return;
  }
  
  // Only allow POST requests//
  if (req.method !== 'POST') {
    console.log('Invalid method:', req.method);
    res.status(405).json({ error: 'Method Not Allowed' });
    return;
  }
  
  try {
    console.log('Request body:', req.body);
    
    const { to, subject, message } = req.body;
    
    // Validate required fields
    if (!to || !message) {
      console.log('Missing required fields');
      res.status(400).json({ 
        error: 'Missing required fields', 
        required: ['to', 'message'],
        received: req.body
      });
      return;
    }
    
    // Prepare email
    const mailOptions = {
      from: 'justinl5872@gmail.com',  // UPDATE: Replace with your actual Gmail
      to: to,                        // This will be like 5551234567@txt.att.net
      subject: subject || 'Alert',
      text: message
    };
    
    console.log('Sending email to:', to);
    console.log('Message:', message);
    
    // Send email
    const result = await transporter.sendMail(mailOptions);
    console.log('Email sent successfully:', result.messageId);
    
    res.status(200).json({
      success: true,
      message: 'SMS sent successfully',
      recipient: to,
      messageId: result.messageId
    });
    
  } catch (error) {
    console.error('Error sending SMS:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      details: error.toString()
    });
  }
});