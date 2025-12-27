import jsPDF from 'jspdf';
import type { Project } from '@/types/project';
import { AGENT_CARDS } from '@/types/project';

const COLORS = {
  primary: [45, 212, 191] as [number, number, number], // Teal
  background: [15, 23, 42] as [number, number, number], // Dark blue
  cardBg: [30, 41, 59] as [number, number, number], // Slate
  text: [241, 245, 249] as [number, number, number], // Light
  muted: [148, 163, 184] as [number, number, number], // Gray
};

function wrapText(text: string, maxWidth: number, pdf: jsPDF): string[] {
  const lines: string[] = [];
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

function addPage(pdf: jsPDF): number {
  pdf.addPage();
  // Add background
  pdf.setFillColor(...COLORS.background);
  pdf.rect(0, 0, pdf.internal.pageSize.getWidth(), pdf.internal.pageSize.getHeight(), 'F');
  return 25;
}

export function exportToPDF(project: Project): void {
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
  pdf.text(`Generated: ${date}  •  Status: ${project.status.toUpperCase()}`, margin, yPosition);
  yPosition += 20;

  // Analysis sections
  const analysisData: Record<string, string | null> = {
    marketAnalysis: project.market_analysis,
    costPrediction: project.cost_prediction,
    businessStrategy: project.business_strategy,
    monetization: project.monetization,
    legalConsiderations: project.legal_considerations,
    techStack: project.tech_stack,
    strategistCritique: project.strategist_critique,
  };

  for (const agent of AGENT_CARDS) {
    const content = analysisData[agent.id];
    if (!content) continue;

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

    // Section content
    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(9);
    pdf.setTextColor(...COLORS.text);
    
    const lines = wrapText(content, contentWidth - 10, pdf);
    
    for (const line of lines) {
      if (yPosition > pageHeight - 20) {
        yPosition = addPage(pdf);
      }
      
      // Check for headers (lines starting with ** or #)
      if (line.startsWith('**') || line.startsWith('#')) {
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(...COLORS.primary);
        pdf.text(line.replace(/\*\*/g, '').replace(/^#+\s*/, ''), margin + 5, yPosition);
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
