function stepSlide(demoLabel, stepNum, totalSteps, title, bullets) {
  const sl = pres.addSlide();
  sl.background = { color: C.LB };
  // Nav bar
  sl.addShape(pres.shapes.RECTANGLE,
    { x:0, y:0, w:10, h:0.65, fill:{color:C.N}, line:{color:C.N} });
  // Step badge
  sl.addShape(pres.shapes.RECTANGLE,
    { x:0.3, y:0.12, w:1.3, h:0.4, fill:{color:C.P}, line:{color:C.P} });
  sl.addText(`${stepNum} / ${totalSteps}`, {
    x:0.3, y:0.12, w:1.3, h:0.4,
    fontSize:13, color:C.W, fontFace:"Calibri", bold:true,
    align:"center", valign:"middle",
  });
  // Demo label + step title
  sl.addText(`${demoLabel}  —  ${title}`, {
    x:1.78, y:0, w:7.9, h:0.65,
    fontSize:14, color:C.W, fontFace:"Calibri", bold:true,
    align:"left", valign:"middle",
  });
  // 3-bullet content
  const items = bullets.map((b, i) => ({
    text: b,
    options: { bullet:true, breakLine: i < bullets.length-1,
      color:C.D, fontSize:15, fontFace:"Calibri", paraSpaceAfter:12 },
  }));
  sl.addText(items, { x:0.45, y:0.82, w:9.0, h:4.35, align:"left", valign:"top" });
  footer(sl);
}
