import { describe, expect, it } from 'vitest'
import { spriteFor } from './sprites'

describe('spriteFor', () => {
  it('monta a URL pelo papel e status', () => {
    const s = spriteFor('qa_engineer', 'working')
    expect(s.url).toBe('/images/sprites/qa_engineer/trabalhando_no_computador.png')
    expect(s.frames).toBe(12)
  })

  it('usa a tira longa quando ocioso', () => {
    expect(spriteFor('tech_lead', 'idle').frames).toBe(24)
  })
})
