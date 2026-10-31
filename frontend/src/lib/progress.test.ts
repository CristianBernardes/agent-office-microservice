import { expect, it } from 'vitest'
import { taskProgress } from './progress'

it('mapeia status para porcentagem crescente no fluxo', () => {
  expect(taskProgress('backlog')).toBe(0)
  expect(taskProgress('in_progress')).toBeLessThan(taskProgress('in_review'))
  expect(taskProgress('done')).toBe(100)
})
