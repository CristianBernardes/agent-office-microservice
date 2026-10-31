import { describe, expect, it } from 'vitest'
import { spriteFor } from './sprites'

describe('spriteFor', () => {
  it('monta a URL pelo papel e status', () => {
    const s = spriteFor('qa_engineer', 'working')
    expect(s.url).toBe('/images/sprites/qa_engineer/trabalhando_no_computador.png')
    expect(s.frames).toBe(12)
  })

  it('usa a folha de deslocamento ao andar', () => {
    const s = spriteFor('dev_junior', 'idle', true)
    expect(s.url).toBe('/images/sprites/dev_junior/deslocamento_entre_salas.png')
    expect(s.frames).toBe(24)
  })

  it('usa a tira longa quando ocioso', () => {
    expect(spriteFor('tech_lead', 'idle').frames).toBe(24)
  })

  it('usa as poses alternativas', () => {
    expect(spriteFor('qa_engineer', 'idle', false, true).url).toContain('interagindo_com_objetos')
    expect(spriteFor('qa_engineer', 'idle', false, true).frames).toBe(48)
    expect(spriteFor('qa_engineer', 'working', false, true).url).toContain('outra_postura_de_trabalho')
    expect(spriteFor('qa_engineer', 'talking', false, true).url).toContain('participando_de_reunioes')
  })
})
