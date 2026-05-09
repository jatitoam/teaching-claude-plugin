const codeBox = (slide, code, x, y, w, h) => {
  slide.addShape(pres.shapes.RECTANGLE,
    { x, y, w, h, fill:{color:"0D1021"}, line:{color:"2E3A59"} });
  slide.addText(code, { x:x+0.15, y:y+0.12, w:w-0.3, h:h-0.24,
    fontSize:10.5, color:"D4D4D8", fontFace:"Courier New",
    align:"left", valign:"top", margin:0 });
};
