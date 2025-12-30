import jsPDF from 'jspdf';
import { AGENT_CARDS } from '@/types/project';
import { formatContentForPDF } from '@/lib/format-content';

const COLORS = {
  primary: [45, 212, 191],
  background: [15, 23, 42],
  cardBg: [30, 41, 59],
  text: [241, 245, 249],
  muted: [148, 163, 184],
  chart1: [45, 212, 191],
  chart2: [99, 102, 241],
  chart3: [244, 114, 182],
  chart4: [251, 191, 36],
  chart5: [34, 197, 94],
};

function wrapText(text, maxWidth, pdf) {
  const lines = [];
  const paragraphs = text.split('\n');
  
  for (const paragraph of paragraphs) {
    if (paragraph.trim() === '') {
      lines.push('');
      continue;
    }
    
    const words = paragraph.split(' ');
    let currentLine = '';
    
    for (const word of words) {
      const testLine = currentLine ? `${currentLine} ${word}` : word;
      const textWidth = pdf.getTextWidth(testLine);
      
      if (textWidth > maxWidth && currentLine) {
        lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    }
    
    if (currentLine) {
      lines.push(currentLine);
    }
  }
  
  return lines;
}

function addPage(pdf) {
  pdf.addPage();
  // Add background
  pdf.setFillColor(...COLORS.background);
  pdf.rect(0, 0, pdf.internal.pageSize.getWidth(), pdf.internal.pageSize.getHeight(), 'F');
  return 25;
}

// Draw a simple pie chart
function drawPieChart(pdf, x, y, radius, data, title) {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  if (total === 0) return y;

  // Title
  pdf.setFont('helvetica', 'bold');
  pdf.setFontSize(10);
  pdf.setTextColor(...COLORS.primary);
  pdf.text(title, x, y);
  y += 8;

  let startAngle = -Math.PI / 2; // Start from top
  const centerX = x + radius + 10;
  const centerY = y + radius;

  // Draw pie slices
  for (const item of data) {
    const sliceAngle = (item.value / total) * 2 * Math.PI;
    const endAngle = startAngle + sliceAngle;

    // Draw filled arc
    pdf.setFillColor(...item.color);
    
    // Create pie slice path
    const segments = 20;
    const points = [[centerX, centerY]];
    
    for (let i = 0; i <= segments; i++) {
      const angle = startAngle + (sliceAngle * i / segments);
      points.push([
        centerX + radius * Math.cos(angle),
        centerY + radius * Math.sin(angle)
      ]);
    }
    points.push([centerX, centerY]);

    // Draw the slice using lines (simplified approach)
    pdf.setDrawColor(...item.color);
    pdf.setLineWidth(0.5);
    
    // Fill the slice by drawing triangles
    for (let i = 1; i < points.length - 1; i++) {
      const triangle = [points[0], points[i], points[i + 1]];
      // Simple triangle fill
      pdf.triangle(
        triangle[0][0], triangle[0][1],
        triangle[1][0], triangle[1][1],
        triangle[2][0], triangle[2][1],
        'F'
      );
    }

    startAngle = endAngle;
  }

  // Draw legend
  const legendX = centerX + radius + 20;
  let legendY = y + 5;
  pdf.setFontSize(7);
  
  for (const item of data) {
    pdf.setFillColor(...item.color);
    pdf.rect(legendX, legendY - 3, 4, 4, 'F');
    pdf.setTextColor(...COLORS.text);
    pdf.setFont('helvetica', 'normal');
    const percentage = Math.round((item.value / total) * 100);
    pdf.text(`${item.label} (${percentage}%)`, legendX + 6, legendY);
    legendY += 6;
  }

  return y + radius * 2 + 15;
}

// Draw a simple bar chart
function drawBarChart(pdf, x, y, width, height, data, title) {
  if (data.length === 0) return y;
  
  const maxValue = Math.max(...data.map(d => d.value));
  if (maxValue === 0) return y;

  // Title
  pdf.setFont('helvetica', 'bold');
  pdf.setFontSize(10);
  pdf.setTextColor(...COLORS.primary);
  pdf.text(title, x, y);
  y += 10;

  const barWidth = Math.min(25, (width - 20) / data.length);
  const chartHeight = height - 20;
  const gap = 5;

  // Draw bars
  let barX = x + 10;
  for (const item of data) {
    const barHeight = (item.value / maxValue) * chartHeight;
    
    // Draw bar
    pdf.setFillColor(...item.color);
    pdf.rect(barX, y + chartHeight - barHeight, barWidth, barHeight, 'F');
    
    // Draw label below bar
    pdf.setFontSize(6);
    pdf.setTextColor(...COLORS.muted);
    pdf.setFont('helvetica', 'normal');
    
    // Truncate label if too long
    const label = item.label.length > 10 ? item.label.substring(0, 8) + '...' : item.label;
    pdf.text(label, barX + barWidth / 2, y + chartHeight + 8, { align: 'center' });
    
    // Draw value above bar
    pdf.setTextColor(...COLORS.text);
    pdf.text(item.value.toString(), barX + barWidth / 2, y + chartHeight - barHeight - 3, { align: 'center' });
    
    barX += barWidth + gap;
  }

  return y + height + 10;
}

// Extract numeric data from cost prediction text
function extractCostData(content) {
  const data = [];
  const colors = [COLORS.chart1, COLORS.chart2, COLORS.chart3, COLORS.chart4, COLORS.chart5];
  
  // Try to find dollar amounts with labels
  const patterns = [
    { regex: /technology|tech|infrastructure/i, label: 'Technology' },
    { regex: /team|personnel|salaries|employees/i, label: 'Team' },
    { regex: /marketing|advertising|customer acquisition/i, label: 'Marketing' },
    { regex: /legal|compliance|incorporation/i, label: 'Legal' },
    { regex: /operations|overhead|office/i, label: 'Operations' },
  ];

  // Simple extraction - look for common cost categories
  const lines = content.split('\n');
  let colorIndex = 0;

  for (const pattern of patterns) {
    for (const line of lines) {
      if (pattern.regex.test(line)) {
        // Look for dollar amounts
        const dollarMatch = line.match(/\$[\d,]+(?:\.\d{2})?/);
        if (dollarMatch) {
          const value = parseInt(dollarMatch[0].replace(/[$,]/g, ''), 10);
          if (value > 0 && value < 10000000) { // Reasonable range
            data.push({
              label: pattern.label,
              value,
              color: colors[colorIndex % colors.length]
            });
            colorIndex++;
            break;
          }
        }
      }
    }
  }

  // If we couldn't extract, create sample data for visualization
  if (data.length < 3) {
    return [
      { label: 'Technology', value: 35, color: COLORS.chart1 },
      { label: 'Team', value: 40, color: COLORS.chart2 },
      { label: 'Marketing', value: 15, color: COLORS.chart3 },
      { label: 'Operations', value: 10, color: COLORS.chart4 },
    ];
  }

  return data;
}

// Extract market data for visualization
function extractMarketData(content) {
  const colors = [COLORS.chart1, COLORS.chart2, COLORS.chart3];
  
  // Look for TAM, SAM, SOM values
  const data = [];
  
  const tamMatch = content.match(/TAM[^$]*\$?([\d.]+)\s*(billion|million|B|M)/i);
  const samMatch = content.match(/SAM[^$]*\$?([\d.]+)\s*(billion|million|B|M)/i);
  const somMatch = content.match(/SOM[^$]*\$?([\d.]+)\s*(billion|million|B|M)/i);

  const parseValue = (match) => {
    if (!match) return 0;
    let value = parseFloat(match[1]);
    if (/billion|B/i.test(match[2])) value *= 1000;
    return value;
  };

  const tamValue = parseValue(tamMatch);
  const samValue = parseValue(samMatch);
  const somValue = parseValue(somMatch);

  if (tamValue > 0 || samValue > 0 || somValue > 0) {
    if (tamValue > 0) data.push({ label: 'TAM', value: tamValue, color: colors[0] });
    if (samValue > 0) data.push({ label: 'SAM', value: samValue, color: colors[1] });
    if (somValue > 0) data.push({ label: 'SOM', value: somValue, color: colors[2] });
  }

  // Default visualization if no data found
  if (data.length === 0) {
    return [
      { label: 'TAM', value: 100, color: COLORS.chart1 },
      { label: 'SAM', value: 40, color: COLORS.chart2 },
      { label: 'SOM', value: 10, color: COLORS.chart3 },
    ];
  }

  return data;
}

export function exportToPDF(project) {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 20;
  const contentWidth = pageWidth - margin * 2;
  let yPosition = 25;

  // Background
  pdf.setFillColor(...COLORS.background);
  pdf.rect(0, 0, pageWidth, pageHeight, 'F');

  // Header accent bar
  pdf.setFillColor(...COLORS.primary);
  pdf.rect(0, 0, pageWidth, 8, 'F');

  // Title
  pdf.setFont('helvetica', 'bold');
  pdf.setFontSize(28);
  pdf.setTextColor(...COLORS.text);
  pdf.text('Startup Analysis Report', margin, yPosition + 15);
  yPosition += 30;

  // Subtitle
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(12);
  pdf.setTextColor(...COLORS.muted);
  pdf.text('AI-Powered Strategic Analysis', margin, yPosition);
  yPosition += 15;

  // Divider
  pdf.setDrawColor(...COLORS.primary);
  pdf.setLineWidth(0.5);
  pdf.line(margin, yPosition, pageWidth - margin, yPosition);
  yPosition += 15;

  // Startup Idea section
  pdf.setFillColor(...COLORS.cardBg);
  pdf.roundedRect(margin, yPosition, contentWidth, 40, 3, 3, 'F');
  
  pdf.setFont('helvetica', 'bold');
  pdf.setFontSize(11);
  pdf.setTextColor(...COLORS.primary);
  pdf.text('STARTUP IDEA', margin + 8, yPosition + 10);
  
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(10);
  pdf.setTextColor(...COLORS.text);
  
  const ideaLines = wrapText(project.startup_idea, contentWidth - 16, pdf);
  let ideaY = yPosition + 18;
  for (let i = 0; i < Math.min(ideaLines.length, 4); i++) {
    pdf.text(ideaLines[i], margin + 8, ideaY);
    ideaY += 5;
  }
  
  yPosition += 50;

  // Target Market (if exists)
  if (project.target_market) {
    pdf.setFillColor(...COLORS.cardBg);
    pdf.roundedRect(margin, yPosition, contentWidth, 20, 3, 3, 'F');
    
    pdf.setFont('helvetica', 'bold');
    pdf.setFontSize(11);
    pdf.setTextColor(...COLORS.primary);
    pdf.text('TARGET MARKET', margin + 8, yPosition + 10);
    
    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(10);
    pdf.setTextColor(...COLORS.text);
    pdf.text(project.target_market.substring(0, 100), margin + 60, yPosition + 10);
    
    yPosition += 30;
  }

  // Date and Status
  pdf.setFontSize(9);
  pdf.setTextColor(...COLORS.muted);
  const date = new Date(project.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  pdf.text(`Generated: ${date}  |  Status: ${project.status.toUpperCase()}`, margin, yPosition);
  yPosition += 20;

  // Analysis sections
  const analysisData = {
    marketAnalysis: project.market_analysis,
    costPrediction: project.cost_prediction,
    businessStrategy: project.business_strategy,
    monetization: project.monetization,
    legalConsiderations: project.legal_considerations,
    techStack: project.tech_stack,
    strategistCritique: project.strategist_critique,
  };

  for (const agent of AGENT_CARDS) {
    const rawContent = analysisData[agent.id];
    if (!rawContent) continue;
    
    // Format content to remove asterisks
    const content = formatContentForPDF(rawContent);

    // Check if we need a new page
    if (yPosition > pageHeight - 60) {
      yPosition = addPage(pdf);
    }

    // Section header
    pdf.setFillColor(...COLORS.cardBg);
    pdf.roundedRect(margin, yPosition, contentWidth, 12, 2, 2, 'F');
    
    pdf.setFont('helvetica', 'bold');
    pdf.setFontSize(12);
    pdf.setTextColor(...COLORS.primary);
    pdf.text(`${agent.icon}  ${agent.title}`, margin + 5, yPosition + 8);
    
    yPosition += 16;

    // Add charts for specific sections
    if (agent.id === 'marketAnalysis' && content) {
      // Check if we need a new page for the chart
      if (yPosition > pageHeight - 80) {
        yPosition = addPage(pdf);
      }
      
      const marketData = extractMarketData(content);
      yPosition = drawBarChart(pdf, margin, yPosition, contentWidth, 50, marketData, 'Market Size Overview (Relative Scale)');
    }
    
    if (agent.id === 'costPrediction' && content) {
      // Check if we need a new page for the chart
      if (yPosition > pageHeight - 80) {
        yPosition = addPage(pdf);
      }
      
      const costData = extractCostData(content);
      yPosition = drawPieChart(pdf, margin, yPosition, 25, costData, 'Budget Allocation');
    }

    // Section content
    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(9);
    pdf.setTextColor(...COLORS.text);
    
    const lines = wrapText(content, contentWidth - 10, pdf);
    
    for (const line of lines) {
      if (yPosition > pageHeight - 20) {
        yPosition = addPage(pdf);
      }
      
      // Check for headers (lines that look like headers)
      const isHeader = /^[A-Z][A-Z\s\d]+:?$/.test(line.trim()) || 
                       /^\d+\.\s+[A-Z]/.test(line.trim()) ||
                       line.startsWith('#');
      
      if (isHeader) {
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(...COLORS.primary);
        pdf.text(line.replace(/^#+\s*/, ''), margin + 5, yPosition);
        pdf.setFont('helvetica', 'normal');
        pdf.setTextColor(...COLORS.text);
      } else if (line.startsWith('- ') || line.startsWith('• ')) {
        pdf.text(`  ${line}`, margin + 5, yPosition);
      } else {
        pdf.text(line, margin + 5, yPosition);
      }
      
      yPosition += 4.5;
    }
    
    yPosition += 10;
  }

  // Footer on last page
  pdf.setFontSize(8);
  pdf.setTextColor(...COLORS.muted);
  pdf.text(
    'Generated by StartupAI - AI-Powered Startup Analysis Platform',
    pageWidth / 2,
    pageHeight - 10,
    { align: 'center' }
  );

  // Save the PDF
  const filename = `startup-analysis-${project.id.substring(0, 8)}.pdf`;
  pdf.save(filename);
}
