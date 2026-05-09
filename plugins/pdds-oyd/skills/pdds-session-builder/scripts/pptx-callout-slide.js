function calloutSlide(title, label, body) {
  const sl = pres.addSlide();
  sl.background = { color: C.N };
  sl.addShape(pres.shapes.RECTANGLE,
    { x:0, y:0, w:10, h:0.55, fill:{color:C.P}, line:{color:C.P} });
  sl.addText(title, {
    x:0.35, y:0, w:9.3, h:0.55,
    fontSize:14, color:C.W, fontFace:"Calibri", bold:true,
    align:"left", valign:"middle",
  });
  sl.addShape(pres.shapes.RECTANGLE,
    { x:0.45, y:0.75, w:9.1, h:4.35, fill:{color:"131A4A"}, line:{color:C.P} });
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE,
    { x:0.75, y:1.0, w:2.8, h:0.42, fill:{color:C.P}, line:{color:C.P}, rectRadius:0.06 });
  sl.addText(label, {
    x:0.75, y:1.0, w:2.8, h:0.42,
    fontSize:11, color:C.W, fontFace:"Calibri", bold:true,
    align:"center", valign:"middle",
  });
  sl.addText(body, {
    x:0.75, y:1.58, w:8.5, h:3.35,
    fontSize:15, color:C.W, fontFace:"Calibri",
    align:"left", valign:"top",
  });
  footer(sl);
}
