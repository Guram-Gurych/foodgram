import { Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  return (
    <Main>
      <MetaTags>
        <title>Технологии</title>
        <meta name="description" content="Фудграм - Технологии" />
        <meta property="og:title" content="Технологии" />
      </MetaTags>

      <Container>
        <div className={styles.content}>
          <div>
            <h1 className={styles.title}>Технологии</h1>
            <h2 className={styles.subtitle}>Что под капотом Foodgram?</h2>

            <p className={`${styles.text} ${styles.textItem}`}>
              Проект построен на современных веб-технологиях, обеспечивающих стабильную работу, масштабируемость и удобство использования.
            </p>

            <ul className={styles.text}>
              <li className={styles.textItem}>
                <strong>Backend:</strong> Python, Django 3.2, Django REST Framework
              </li>
              <li className={styles.textItem}>
                <strong>Авторизация:</strong> Djoser
              </li>
              <li className={styles.textItem}>
                <strong>База данных:</strong> PostgreSQL
              </li>
              <li className={styles.textItem}>
                <strong>Контейнеризация:</strong> Docker
              </li>
              <li className={styles.textItem}>
                <strong>Frontend:</strong> React
              </li>
              <li className={styles.textItem}>
                <strong>Веб-сервер:</strong> Gunicorn + Nginx
              </li>
              <li className={styles.textItem}>
                <strong>CI/CD:</strong> GitHub Actions
              </li>
            </ul>
          </div>
        </div>
      </Container>
    </Main>
  )
}

export default Technologies
