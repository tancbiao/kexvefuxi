/**
 * generate_xuanba.js - 预生成校队选拔60道固定题目
 * 基于 MIT 开源 rpm-iq-exam 的 puzzleGenerator 移植
 * 使用固定种子确保每次生成相同题目
 */

// ========== Seeded PRNG (Mulberry32) ==========
var _seed = 20260603;
function seededRandom() {
  _seed |= 0;
  _seed = _seed + 0x6D2B79F5 | 0;
  var t = Math.imul(_seed ^ _seed >>> 15, 1 | _seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
  return ((t ^ t >>> 14) >>> 0) / 4294967296;
}

function seededShuffle(arr) {
  var a = arr.slice();
  for (var i = a.length - 1; i > 0; i--) {
    var j = (seededRandom() * (i + 1)) | 0;
    var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
  }
  return a;
}

// ========== Shape/Pattern creation ==========
var shapeTypes = ['circle', 'square', 'triangle', 'diamond', 'cross', 'star'];
var sizes = ['small', 'medium', 'large'];
var colors = ['black', 'gray', 'white'];

function createRandomShape(overrides) {
  overrides = overrides || {};
  return {
    type: overrides.type || shapeTypes[(seededRandom() * shapeTypes.length) | 0],
    size: overrides.size || sizes[(seededRandom() * sizes.length) | 0],
    color: overrides.color || colors[(seededRandom() * colors.length) | 0],
    rotation: overrides.rotation || 0,
    position: overrides.position || { x: 0.5, y: 0.5 }
  };
}

// ========== Puzzle generators (ported from TypeScript) ==========

function generateLevel1Puzzle(puzzleIndex) {
  var idx = puzzleIndex % 5;
  // Type 0: Size progression
  if (idx === 0) {
    var bs = createRandomShape({ position: { x: 0.5, y: 0.5 } });
    var matrix = [
      [{ shapes: [extend(bs, { size: 'small' })] }, { shapes: [extend(bs, { size: 'medium' })] }, { shapes: [extend(bs, { size: 'large' })] }],
      [{ shapes: [extend(bs, { size: 'medium' })] }, { shapes: [extend(bs, { size: 'large' })] }, { shapes: [extend(bs, { size: 'small' })] }],
      [{ shapes: [extend(bs, { size: 'large' })] }, { shapes: [extend(bs, { size: 'small' })] }, null]
    ];
    var correct = { shapes: [extend(bs, { size: 'medium' })] };
    var options = seededShuffle([
      correct, { shapes: [extend(bs, { size: 'small' })] }, { shapes: [extend(bs, { size: 'large' })] },
      { shapes: [extend(bs, { type: 'circle' })] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // Type 1: Shape rotation
  if (idx === 1) {
    var bs = createRandomShape({ type: 'triangle', position: { x: 0.5, y: 0.5 } });
    var matrix = [
      [{ shapes: [extend(bs, { rotation: 0 })] }, { shapes: [extend(bs, { rotation: 90 })] }, { shapes: [extend(bs, { rotation: 180 })] }],
      [{ shapes: [extend(bs, { rotation: 90 })] }, { shapes: [extend(bs, { rotation: 180 })] }, { shapes: [extend(bs, { rotation: 270 })] }],
      [{ shapes: [extend(bs, { rotation: 180 })] }, { shapes: [extend(bs, { rotation: 270 })] }, null]
    ];
    var correct = { shapes: [extend(bs, { rotation: 0 })] };
    var options = seededShuffle([
      correct, { shapes: [extend(bs, { rotation: 90 })] }, { shapes: [extend(bs, { rotation: 180 })] },
      { shapes: [extend(bs, { rotation: 270 })] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // Type 2: Color progression
  if (idx === 2) {
    var bs = createRandomShape({ position: { x: 0.5, y: 0.5 } });
    var matrix = [
      [{ shapes: [extend(bs, { color: 'black' })] }, { shapes: [extend(bs, { color: 'gray' })] }, { shapes: [extend(bs, { color: 'white' })] }],
      [{ shapes: [extend(bs, { color: 'gray' })] }, { shapes: [extend(bs, { color: 'white' })] }, { shapes: [extend(bs, { color: 'black' })] }],
      [{ shapes: [extend(bs, { color: 'white' })] }, { shapes: [extend(bs, { color: 'black' })] }, null]
    ];
    var correct = { shapes: [extend(bs, { color: 'gray' })] };
    var options = seededShuffle([
      correct, { shapes: [extend(bs, { color: 'black' })] }, { shapes: [extend(bs, { color: 'white' })] },
      { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // Type 3: Shape sequence
  if (idx === 3) {
    var s = [
      createRandomShape({ type: 'circle', position: { x: 0.5, y: 0.5 } }),
      createRandomShape({ type: 'square', position: { x: 0.5, y: 0.5 } }),
      createRandomShape({ type: 'triangle', position: { x: 0.5, y: 0.5 } })
    ];
    var matrix = [
      [{ shapes: [s[0]] }, { shapes: [s[1]] }, { shapes: [s[2]] }],
      [{ shapes: [s[1]] }, { shapes: [s[2]] }, { shapes: [s[0]] }],
      [{ shapes: [s[2]] }, { shapes: [s[0]] }, null]
    ];
    var correct = { shapes: [s[1]] };
    var options = seededShuffle([
      correct, { shapes: [s[0]] }, { shapes: [s[2]] },
      { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // Type 4: Addition pattern
  var s1 = createRandomShape({ position: { x: 0.3, y: 0.5 } });
  var s2 = createRandomShape({ position: { x: 0.7, y: 0.5 } });
  var matrix = [
    [{ shapes: [s1] }, { shapes: [s2] }, { shapes: [s1, s2] }],
    [{ shapes: [s2] }, { shapes: [s1] }, { shapes: [s1, s2] }],
    [{ shapes: [s1] }, { shapes: [s2] }, null]
  ];
  var correct = { shapes: [s1, s2] };
  var options = seededShuffle([
    correct, { shapes: [s1] }, { shapes: [s2] },
    { shapes: [createRandomShape(), createRandomShape()] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
  ]);
  return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
}

function generateLevel2Puzzle(puzzleIndex) {
  var idx = puzzleIndex % 5;
  if (idx === 0) {
    var bs = createRandomShape({ type: 'diamond', position: { x: 0.5, y: 0.5 } });
    var matrix = [
      [{ shapes: [extend(bs, { size: 'small', rotation: 0 })] }, { shapes: [extend(bs, { size: 'medium', rotation: 45 })] }, { shapes: [extend(bs, { size: 'large', rotation: 90 })] }],
      [{ shapes: [extend(bs, { size: 'medium', rotation: 45 })] }, { shapes: [extend(bs, { size: 'large', rotation: 90 })] }, { shapes: [extend(bs, { size: 'small', rotation: 135 })] }],
      [{ shapes: [extend(bs, { size: 'large', rotation: 90 })] }, { shapes: [extend(bs, { size: 'small', rotation: 135 })] }, null]
    ];
    var correct = { shapes: [extend(bs, { size: 'medium', rotation: 180 })] };
    var options = seededShuffle([
      correct, { shapes: [extend(bs, { size: 'medium', rotation: 45 })] }, { shapes: [extend(bs, { size: 'large', rotation: 180 })] },
      { shapes: [extend(bs, { size: 'small', rotation: 180 })] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  if (idx === 1) {
    var s1 = createRandomShape({ type: 'circle', position: { x: 0.3, y: 0.3 } });
    var s2 = createRandomShape({ type: 'square', position: { x: 0.7, y: 0.7 } });
    var matrix = [
      [{ shapes: [extend(s1, { size: 'small' }), extend(s2, { size: 'large' })] }, { shapes: [extend(s1, { size: 'medium' }), extend(s2, { size: 'medium' })] }, { shapes: [extend(s1, { size: 'large' }), extend(s2, { size: 'small' })] }],
      [{ shapes: [extend(s1, { size: 'medium' }), extend(s2, { size: 'medium' })] }, { shapes: [extend(s1, { size: 'large' }), extend(s2, { size: 'small' })] }, { shapes: [extend(s1, { size: 'small' }), extend(s2, { size: 'large' })] }],
      [{ shapes: [extend(s1, { size: 'large' }), extend(s2, { size: 'small' })] }, { shapes: [extend(s1, { size: 'small' }), extend(s2, { size: 'large' })] }, null]
    ];
    var correct = { shapes: [extend(s1, { size: 'medium' }), extend(s2, { size: 'medium' })] };
    var options = seededShuffle([
      correct, { shapes: [extend(s1, { size: 'large' }), extend(s2, { size: 'small' })] }, { shapes: [extend(s1, { size: 'small' }), extend(s2, { size: 'large' })] },
      { shapes: [extend(s1, { size: 'medium' }), extend(s2, { size: 'large' })] }, { shapes: [createRandomShape(), createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  if (idx === 2) {
    var m = [
      [{ shapes: [{ type: 'circle', size: 'medium', color: 'black', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, { shapes: [{ type: 'square', size: 'medium', color: 'gray', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, { shapes: [{ type: 'triangle', size: 'medium', color: 'white', rotation: 0, position: { x: 0.5, y: 0.5 } }] }],
      [{ shapes: [{ type: 'square', size: 'medium', color: 'gray', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, { shapes: [{ type: 'triangle', size: 'medium', color: 'white', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, { shapes: [{ type: 'circle', size: 'medium', color: 'black', rotation: 0, position: { x: 0.5, y: 0.5 } }] }],
      [{ shapes: [{ type: 'triangle', size: 'medium', color: 'white', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, { shapes: [{ type: 'circle', size: 'medium', color: 'black', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, null]
    ];
    var correct = { shapes: [{ type: 'square', size: 'medium', color: 'gray', rotation: 0, position: { x: 0.5, y: 0.5 } }] };
    var options = seededShuffle([
      correct, { shapes: [{ type: 'circle', size: 'medium', color: 'gray', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, { shapes: [{ type: 'square', size: 'medium', color: 'black', rotation: 0, position: { x: 0.5, y: 0.5 } }] },
      { shapes: [{ type: 'triangle', size: 'medium', color: 'gray', rotation: 0, position: { x: 0.5, y: 0.5 } }] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: m, options: options, correct: findCorrect(options, correct) };
  }
  if (idx === 3) {
    var bs = createRandomShape({ type: 'star' });
    var matrix = [
      [{ shapes: [extend(bs, { position: { x: 0.3, y: 0.3 }, rotation: 0 })] }, { shapes: [extend(bs, { position: { x: 0.7, y: 0.3 }, rotation: 60 })] }, { shapes: [extend(bs, { position: { x: 0.5, y: 0.7 }, rotation: 120 })] }],
      [{ shapes: [extend(bs, { position: { x: 0.7, y: 0.3 }, rotation: 60 })] }, { shapes: [extend(bs, { position: { x: 0.5, y: 0.7 }, rotation: 120 })] }, { shapes: [extend(bs, { position: { x: 0.3, y: 0.3 }, rotation: 180 })] }],
      [{ shapes: [extend(bs, { position: { x: 0.5, y: 0.7 }, rotation: 120 })] }, { shapes: [extend(bs, { position: { x: 0.3, y: 0.3 }, rotation: 180 })] }, null]
    ];
    var correct = { shapes: [extend(bs, { position: { x: 0.7, y: 0.3 }, rotation: 240 })] };
    var options = seededShuffle([
      correct, { shapes: [extend(bs, { position: { x: 0.7, y: 0.3 }, rotation: 60 })] }, { shapes: [extend(bs, { position: { x: 0.5, y: 0.5 }, rotation: 240 })] },
      { shapes: [extend(bs, { position: { x: 0.7, y: 0.7 }, rotation: 240 })] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // Type 5: Complex addition
  var s1 = createRandomShape({ type: 'circle', position: { x: 0.25, y: 0.5 } });
  var s2 = createRandomShape({ type: 'square', position: { x: 0.75, y: 0.5 } });
  var s3 = createRandomShape({ type: 'triangle', position: { x: 0.5, y: 0.25 } });
  var matrix = [
    [{ shapes: [s1, s3] }, { shapes: [s2] }, { shapes: [s1, s2, s3] }],
    [{ shapes: [s2, s3] }, { shapes: [s1] }, { shapes: [s1, s2, s3] }],
    [{ shapes: [s1] }, { shapes: [s2, s3] }, null]
  ];
  var correct = { shapes: [s1, s2, s3] };
  var options = seededShuffle([
    correct, { shapes: [s1, s2] }, { shapes: [s2, s3] }, { shapes: [s1, s3] }, { shapes: [s1] }, { shapes: [createRandomShape()] }
  ]);
  return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
}

function generateLevel3Puzzle(puzzleIndex) {
  var idx = puzzleIndex % 5;
  if (idx === 0) {
    var bs = createRandomShape({ type: 'cross' });
    var matrix = [
      [{ shapes: [extend(bs, { size: 'small', color: 'black', rotation: 0, position: { x: 0.5, y: 0.5 } })] }, { shapes: [extend(bs, { size: 'medium', color: 'gray', rotation: 45, position: { x: 0.5, y: 0.5 } })] }, { shapes: [extend(bs, { size: 'large', color: 'white', rotation: 90, position: { x: 0.5, y: 0.5 } })] }],
      [{ shapes: [extend(bs, { size: 'medium', color: 'gray', rotation: 45, position: { x: 0.5, y: 0.5 } })] }, { shapes: [extend(bs, { size: 'large', color: 'white', rotation: 90, position: { x: 0.5, y: 0.5 } })] }, { shapes: [extend(bs, { size: 'small', color: 'black', rotation: 135, position: { x: 0.5, y: 0.5 } })] }],
      [{ shapes: [extend(bs, { size: 'large', color: 'white', rotation: 90, position: { x: 0.5, y: 0.5 } })] }, { shapes: [extend(bs, { size: 'small', color: 'black', rotation: 135, position: { x: 0.5, y: 0.5 } })] }, null]
    ];
    var correct = { shapes: [extend(bs, { size: 'medium', color: 'gray', rotation: 180, position: { x: 0.5, y: 0.5 } })] };
    var options = seededShuffle([
      correct, { shapes: [extend(bs, { size: 'medium', color: 'black', rotation: 180, position: { x: 0.5, y: 0.5 } })] }, { shapes: [extend(bs, { size: 'large', color: 'gray', rotation: 180, position: { x: 0.5, y: 0.5 } })] },
      { shapes: [extend(bs, { size: 'medium', color: 'gray', rotation: 135, position: { x: 0.5, y: 0.5 } })] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  if (idx === 1) {
    var s1 = createRandomShape({ type: 'circle' });
    var s2 = createRandomShape({ type: 'square' });
    var s3 = createRandomShape({ type: 'triangle' });
    var matrix = [
      [{ shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'small' })] },
       { shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'small' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'medium' })] },
       { shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'small' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'medium' }), extend(s3, { position: { x: 0.5, y: 0.7 }, size: 'large' })] }],
      [{ shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'medium' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'small' })] },
       { shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'medium' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'small' }), extend(s3, { position: { x: 0.5, y: 0.7 }, size: 'large' })] },
       { shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'medium' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'small' }), extend(s3, { position: { x: 0.5, y: 0.7 }, size: 'large' }), extend(s1, { position: { x: 0.7, y: 0.7 }, size: 'small' })] }],
      [{ shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'large' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'medium' }), extend(s3, { position: { x: 0.5, y: 0.7 }, size: 'small' })] },
       { shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'large' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'medium' }), extend(s3, { position: { x: 0.5, y: 0.7 }, size: 'small' }), extend(s2, { position: { x: 0.3, y: 0.7 }, size: 'large' })] },
       null]
    ];
    var correct = { shapes: [
      extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'large' }),
      extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'medium' }),
      extend(s3, { position: { x: 0.5, y: 0.7 }, size: 'small' }),
      extend(s2, { position: { x: 0.3, y: 0.7 }, size: 'large' }),
      extend(s3, { position: { x: 0.7, y: 0.7 }, size: 'medium' })
    ]};
    var options = seededShuffle([
      correct,
      { shapes: [extend(s1, { position: { x: 0.3, y: 0.3 }, size: 'large' }), extend(s2, { position: { x: 0.7, y: 0.3 }, size: 'medium' }), extend(s3, { position: { x: 0.5, y: 0.7 }, size: 'small' })] },
      { shapes: [createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // idx 2-4: generate unique puzzles with progressive complexity
  if (idx === 2) {
    // Pattern: alternating size + shape progression
    var bs = createRandomShape({ type: 'diamond' });
    var shapes = ['circle', 'square', 'triangle'];
    var matrix = [];
    for (var r = 0; r < 3; r++) {
      matrix[r] = [];
      for (var c = 0; c < 3; c++) {
        if (r === 2 && c === 2) { matrix[r][c] = null; continue; }
        var si = (r + c) % 3;
        var sz = sizes[(r + c) % 3];
        matrix[r][c] = { shapes: [extend(bs, { type: shapes[si], size: sz, rotation: (r + c) * 45, position: { x: 0.5, y: 0.5 } })] };
      }
    }
    var correct = { shapes: [extend(bs, { type: shapes[2], size: sizes[1], rotation: 180, position: { x: 0.5, y: 0.5 } })] };
    var options = seededShuffle([
      correct,
      { shapes: [extend(bs, { type: shapes[0], size: sizes[2], rotation: 180, position: { x: 0.5, y: 0.5 } })] },
      { shapes: [extend(bs, { type: shapes[1], size: sizes[0], rotation: 180, position: { x: 0.5, y: 0.5 } })] },
      { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  if (idx === 3) {
    // Pattern: 2-shape complement (one grows, one shrinks)
    var sa = createRandomShape({ type: 'circle' });
    var sb = createRandomShape({ type: 'square' });
    var matrix = [];
    for (var r = 0; r < 3; r++) {
      matrix[r] = [];
      for (var c = 0; c < 3; c++) {
        if (r === 2 && c === 2) { matrix[r][c] = null; continue; }
        var saIdx = (r + c) % 3;
        var sbIdx = 2 - ((r + c) % 3);
        matrix[r][c] = { shapes: [
          extend(sa, { size: sizes[saIdx], position: { x: 0.3, y: 0.5 } }),
          extend(sb, { size: sizes[sbIdx], position: { x: 0.7, y: 0.5 } })
        ]};
      }
    }
    var correct = { shapes: [
      extend(sa, { size: sizes[1], position: { x: 0.3, y: 0.5 } }),
      extend(sb, { size: sizes[1], position: { x: 0.7, y: 0.5 } })
    ]};
    var options = seededShuffle([
      correct,
      { shapes: [extend(sa, { size: sizes[0], position: { x: 0.3, y: 0.5 } }), extend(sb, { size: sizes[2], position: { x: 0.7, y: 0.5 } })] },
      { shapes: [extend(sa, { size: sizes[2], position: { x: 0.3, y: 0.5 } }), extend(sb, { size: sizes[0], position: { x: 0.7, y: 0.5 } })] },
      { shapes: [createRandomShape(), createRandomShape()] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // idx 4: three-rule transformation
  var bs = createRandomShape({ type: 'star' });
  var matrix = [];
  for (var r = 0; r < 3; r++) {
    matrix[r] = [];
    for (var c = 0; c < 3; c++) {
      if (r === 2 && c === 2) { matrix[r][c] = null; continue; }
      var idx = r * 3 + c;
      matrix[r][c] = { shapes: [extend(bs, {
        size: sizes[idx % 3],
        color: colors[Math.floor(idx / 3) % 3],
        rotation: idx * 30,
        position: { x: 0.5, y: 0.5 }
      })]};
    }
  }
  var correct = { shapes: [extend(bs, { size: sizes[2], color: colors[2], rotation: 240, position: { x: 0.5, y: 0.5 } })] };
  var options = seededShuffle([
    correct,
    { shapes: [extend(bs, { size: sizes[0], color: colors[2], rotation: 240, position: { x: 0.5, y: 0.5 } })] },
    { shapes: [extend(bs, { size: sizes[2], color: colors[0], rotation: 240, position: { x: 0.5, y: 0.5 } })] },
    { shapes: [extend(bs, { size: sizes[2], color: colors[2], rotation: 0, position: { x: 0.5, y: 0.5 } })] },
    { shapes: [createRandomShape()] }, { shapes: [createRandomShape()] }
  ]);
  return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
}

// Levels 4-6: fewer unique types, rest are variations of lower levels with added complexity
function generateLevel4Puzzle(puzzleIndex) {
  var idx = puzzleIndex % 6;
  if (idx === 0) return generateLevel3Puzzle(2); // reuse L3 patterns
  if (idx === 1) return generateLevel3Puzzle(3);
  if (idx === 2) return generateLevel3Puzzle(4);
  // idx 3-5: new L4-specific complex patterns
  if (idx === 3) {
    // 4-corner pattern matrix
    var s = [
      createRandomShape({ type: 'circle', position: { x: 0.25, y: 0.25 } }),
      createRandomShape({ type: 'square', position: { x: 0.75, y: 0.25 } }),
      createRandomShape({ type: 'triangle', position: { x: 0.25, y: 0.75 } }),
      createRandomShape({ type: 'diamond', position: { x: 0.75, y: 0.75 } })
    ];
    var matrix = [];
    for (var r = 0; r < 3; r++) {
      matrix[r] = [];
      for (var c = 0; c < 3; c++) {
        if (r === 2 && c === 2) { matrix[r][c] = null; continue; }
        var count = (r + c) % 4 + 1;
        var cellShapes = [];
        for (var k = 0; k < count; k++) {
          cellShapes.push(extend(s[k % 4], { size: sizes[(r + c + k) % 3], rotation: (r + c + k) * 45 }));
        }
        matrix[r][c] = { shapes: cellShapes };
      }
    }
    var correct = { shapes: [
      extend(s[0], { size: sizes[2], rotation: 30 * 9 }),
      extend(s[1], { size: sizes[0], rotation: 30 * 10 }),
      extend(s[2], { size: sizes[1], rotation: 30 * 11 })
    ]};
    var options = seededShuffle([
      correct,
      { shapes: [extend(s[0], { size: sizes[0], rotation: 270 }), extend(s[1], { size: sizes[1], rotation: 315 })] },
      { shapes: [extend(s[0], { size: sizes[1], rotation: 270 }), extend(s[1], { size: sizes[2], rotation: 315 }), extend(s[2], { size: sizes[0], rotation: 0 }), extend(s[3], { size: sizes[1], rotation: 45 })] },
      { shapes: [createRandomShape(), createRandomShape()] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape(), createRandomShape(), createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  if (idx === 4) {
    // Symmetry-breaking pattern
    var shapes = ['circle', 'square', 'triangle', 'diamond', 'star'];
    var matrix = [];
    for (var r = 0; r < 3; r++) {
      matrix[r] = [];
      for (var c = 0; c < 3; c++) {
        if (r === 2 && c === 2) { matrix[r][c] = null; continue; }
        var idx2 = (r * 3 + c);
        if (idx2 < 4) {
          matrix[r][c] = { shapes: [{ type: shapes[idx2 % 5], size: 'medium', color: 'black', rotation: idx2 * 30, position: { x: 0.5, y: 0.5 } }] };
        } else {
          var cnt = idx2 === 4 ? 2 : (idx2 === 6 ? 2 : 3);
          var cellShapes = [];
          for (var k = 0; k < cnt; k++) {
            cellShapes.push({ type: shapes[(idx2 + k) % 5], size: sizes[k % 3], color: colors[(idx2 + k) % 3], rotation: (idx2 + k) * 45, position: { x: 0.25 + 0.25 * k, y: 0.5 } });
          }
          matrix[r][c] = { shapes: cellShapes };
        }
      }
    }
    var correct = { shapes: [
      { type: shapes[1], size: sizes[2], color: colors[2], rotation: 315, position: { x: 0.25, y: 0.5 } },
      { type: shapes[2], size: sizes[0], color: colors[0], rotation: 0, position: { x: 0.75, y: 0.5 } }
    ]};
    var options = seededShuffle([
      correct,
      { shapes: [{ type: shapes[3], size: sizes[2], color: colors[2], rotation: 315, position: { x: 0.25, y: 0.5 } }, { type: shapes[4], size: sizes[0], color: colors[0], rotation: 0, position: { x: 0.75, y: 0.5 } }] },
      { shapes: [{ type: shapes[1], size: sizes[0], color: colors[1], rotation: 315, position: { x: 0.25, y: 0.5 } }] },
      { shapes: [createRandomShape(), createRandomShape()] }, { shapes: [createRandomShape()] }, { shapes: [createRandomShape(), createRandomShape(), createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // idx 5: recursion pattern
  return generateLevel4Puzzle(3); // fallback
}

function generateLevel5Puzzle(puzzleIndex) {
  var idx = puzzleIndex % 6;
  if (idx === 0) return generateLevel4Puzzle(3);
  if (idx === 1) return generateLevel4Puzzle(4);
  if (idx === 2) {
    // Fibonacci-like shape count pattern
    var s = [
      createRandomShape({ type: 'circle' }),
      createRandomShape({ type: 'square' }),
      createRandomShape({ type: 'triangle' }),
      createRandomShape({ type: 'diamond' }),
      createRandomShape({ type: 'star' })
    ];
    var matrix = [
      [
        { shapes: [extend(s[0], { position: { x: 0.5, y: 0.5 }, size: 'small', color: 'black' })] },
        { shapes: [extend(s[1], { position: { x: 0.5, y: 0.5 }, size: 'small', color: 'black' })] },
        { shapes: [extend(s[0], { position: { x: 0.3, y: 0.5 }, size: 'small', color: 'black' }), extend(s[1], { position: { x: 0.7, y: 0.5 }, size: 'small', color: 'gray' })] }
      ],
      [
        { shapes: [extend(s[1], { position: { x: 0.5, y: 0.5 }, size: 'medium', color: 'gray' })] },
        { shapes: [extend(s[0], { position: { x: 0.3, y: 0.5 }, size: 'small', color: 'gray' }), extend(s[1], { position: { x: 0.7, y: 0.5 }, size: 'medium', color: 'white' })] },
        { shapes: [extend(s[1], { position: { x: 0.2, y: 0.3 }, size: 'medium', color: 'gray' }), extend(s[0], { position: { x: 0.5, y: 0.5 }, size: 'small', color: 'white' }), extend(s[1], { position: { x: 0.8, y: 0.7 }, size: 'large', color: 'black' })] }
      ],
      [
        { shapes: [extend(s[0], { position: { x: 0.3, y: 0.5 }, size: 'medium', color: 'white' }), extend(s[1], { position: { x: 0.7, y: 0.5 }, size: 'large', color: 'black' })] },
        { shapes: [extend(s[1], { position: { x: 0.2, y: 0.3 }, size: 'large', color: 'white' }), extend(s[0], { position: { x: 0.5, y: 0.5 }, size: 'medium', color: 'black' }), extend(s[1], { position: { x: 0.8, y: 0.7 }, size: 'small', color: 'gray' })] },
        null
      ]
    ];
    var correct = { shapes: [
      extend(s[0], { position: { x: 0.15, y: 0.2 }, size: 'large', color: 'black' }),
      extend(s[1], { position: { x: 0.4, y: 0.4 }, size: 'medium', color: 'gray' }),
      extend(s[0], { position: { x: 0.6, y: 0.6 }, size: 'small', color: 'white' }),
      extend(s[1], { position: { x: 0.85, y: 0.8 }, size: 'medium', color: 'black' }),
      extend(s[2], { position: { x: 0.5, y: 0.1 }, size: 'small', color: 'gray' })
    ]};
    var options = seededShuffle([
      correct,
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  // More complex patterns
  if (idx === 3) {
    // Alternating complement
    var a = createRandomShape({ type: 'circle' }), b = createRandomShape({ type: 'square' }), c = createRandomShape({ type: 'triangle' });
    var matrix = [];
    for (var r = 0; r < 3; r++) {
      matrix[r] = [];
      for (var cc = 0; cc < 3; cc++) {
        if (r === 2 && cc === 2) { matrix[r][cc] = null; continue; }
        var n = (r + 1) * (cc + 1);
        var cellShapes = [];
        for (var k = 0; k < n; k++) {
          var s = [a, b, c][k % 3];
          cellShapes.push(extend(s, { size: sizes[(r + cc + k) % 3], color: colors[k % 3], rotation: (r + cc + k) * 30, position: { x: 0.2 + 0.2 * k, y: 0.3 + 0.2 * (k % 3) } }));
        }
        matrix[r][cc] = { shapes: cellShapes };
      }
    }
    var correct = { shapes: [
      extend(a, { size: sizes[2], color: colors[0], rotation: 270, position: { x: 0.2, y: 0.3 } }),
      extend(b, { size: sizes[0], color: colors[1], rotation: 300, position: { x: 0.4, y: 0.5 } }),
      extend(c, { size: sizes[1], color: colors[2], rotation: 330, position: { x: 0.6, y: 0.7 } }),
      extend(a, { size: sizes[2], color: colors[0], rotation: 0, position: { x: 0.8, y: 0.3 } }),
      extend(b, { size: sizes[0], color: colors[1], rotation: 30, position: { x: 0.3, y: 0.7 } }),
      extend(c, { size: sizes[1], color: colors[2], rotation: 60, position: { x: 0.7, y: 0.3 } })
    ]};
    var options = seededShuffle([
      correct,
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  if (idx >= 4) return generateLevel4Puzzle(3 + (idx - 4));
  return generateLevel4Puzzle(3);
}

function generateLevel6Puzzle(puzzleIndex) {
  var idx = puzzleIndex % 5;
  if (idx === 0) {
    // Ultra-complex: 6 shapes, multi-attribute recursion
    var allS = [];
    for (var i = 0; i < 6; i++) allS.push(createRandomShape({ type: shapeTypes[i] }));
    var matrix = [];
    for (var r = 0; r < 3; r++) {
      matrix[r] = [];
      for (var c = 0; c < 3; c++) {
        if (r === 2 && c === 2) { matrix[r][c] = null; continue; }
        var cnt = (r + 1) * (c + 1) + r;
        var cellShapes = [];
        for (var k = 0; k < cnt; k++) {
          cellShapes.push(extend(allS[k % 6], {
            size: sizes[(r + c + k) % 3],
            color: colors[(r * c + k) % 3],
            rotation: (r * 60 + c * 45 + k * 30) % 360,
            position: { x: 0.15 + 0.15 * (k % 5), y: 0.2 + 0.2 * Math.floor(k / 5) }
          }));
        }
        matrix[r][c] = { shapes: cellShapes };
      }
    }
    var correct = { shapes: [
      extend(allS[2], { size: sizes[1], color: colors[0], rotation: 300, position: { x: 0.15, y: 0.2 } }),
      extend(allS[3], { size: sizes[2], color: colors[1], rotation: 0, position: { x: 0.3, y: 0.4 } }),
      extend(allS[4], { size: sizes[0], color: colors[2], rotation: 60, position: { x: 0.45, y: 0.6 } }),
      extend(allS[5], { size: sizes[1], color: colors[0], rotation: 120, position: { x: 0.6, y: 0.2 } }),
      extend(allS[0], { size: sizes[2], color: colors[1], rotation: 180, position: { x: 0.75, y: 0.4 } }),
      extend(allS[1], { size: sizes[0], color: colors[2], rotation: 240, position: { x: 0.15, y: 0.8 } })
    ]};
    var options = seededShuffle([
      correct,
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape(), createRandomShape()] },
      { shapes: [createRandomShape(), createRandomShape()] }
    ]);
    return { matrix: matrix, options: options, correct: findCorrect(options, correct) };
  }
  return generateLevel5Puzzle(idx);
}

// ========== Helpers ==========
function extend(base, overrides) {
  var result = {};
  for (var k in base) result[k] = base[k];
  for (var k in overrides) result[k] = overrides[k];
  return result;
}

function findCorrect(options, correctPattern) {
  var correctStr = JSON.stringify(correctPattern);
  for (var i = 0; i < options.length; i++) {
    if (JSON.stringify(options[i]) === correctStr) return i;
  }
  return 0;
}

// ========== Generate 60 puzzles ==========
function generateAll() {
  _seed = 20260603; // Fixed seed
  var puzzles = [];
  var puzzleId = 1;
  for (var level = 1; level <= 6; level++) {
    for (var i = 0; i < 10; i++) {
      var generator;
      if (level === 1) generator = generateLevel1Puzzle;
      else if (level === 2) generator = generateLevel2Puzzle;
      else if (level === 3) generator = generateLevel3Puzzle;
      else if (level === 4) generator = generateLevel4Puzzle;
      else if (level === 5) generator = generateLevel5Puzzle;
      else generator = generateLevel6Puzzle;
      
      var p = generator(i);
      puzzles.push({
        id: puzzleId,
        level: level,
        typeIndex: i % 6,
        matrix: p.matrix,
        options: p.options,
        correct: p.correct
      });
      puzzleId++;
    }
  }
  return puzzles;
}

// ========== Output ==========
var puzzles = generateAll();
var fs = require('fs');
var output = '// xuanba-questions.js - 校队选拔推理题库（60题，MIT开源算法生成）\n';
output += '// 基于 yuis-ice/rpm-iq-exam puzzleGenerator 移植\n';
output += '// 固定种子 20260603，题目确定性不变\n';
output += '// 生成时间: ' + new Date().toISOString() + '\n';
output += '// 题量: ' + puzzles.length + ' 题，6个等级各10题\n';
output += 'var XUANBA_QUESTIONS = ' + JSON.stringify(puzzles, null, 2) + ';\n';

var path = 'D:/kexvefuxi/data/xuanba-questions.js';
fs.writeFileSync(path, output, 'utf-8');

console.log('Generated ' + puzzles.length + ' puzzles');
console.log('  Level 1 (Basic): ' + puzzles.filter(function(p) { return p.level === 1; }).length + ' puzzles');
console.log('  Level 2 (Simple): ' + puzzles.filter(function(p) { return p.level === 2; }).length + ' puzzles');
console.log('  Level 3 (Moderate): ' + puzzles.filter(function(p) { return p.level === 3; }).length + ' puzzles');
console.log('  Level 4 (Advanced): ' + puzzles.filter(function(p) { return p.level === 4; }).length + ' puzzles');
console.log('  Level 5 (Complex): ' + puzzles.filter(function(p) { return p.level === 5; }).length + ' puzzles');
console.log('  Level 6 (Expert): ' + puzzles.filter(function(p) { return p.level === 6; }).length + ' puzzles');
console.log('Output: ' + path);

// Verify uniqueness
var hashes = {};
var duplicates = 0;
puzzles.forEach(function(p) {
  var h = JSON.stringify(p.matrix);
  if (hashes[h]) duplicates++;
  else hashes[h] = true;
});
console.log('Unique matrices: ' + (60 - duplicates) + ' / ' + 60);
