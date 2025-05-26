import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = () => {
  return (
    <Main>
      <MetaTags>
        <title>О проекте</title>
        <meta name="description" content="Фудграм - О проекте" />
        <meta property="og:title" content="О проекте" />
      </MetaTags>

      <Container>
        <div className={styles.content}>
          <div>
            <h1 className={styles.title}>О проекте</h1>
            <h2 className={styles.subtitle}>Добро пожаловать в Foodgram!</h2>

            <p className={`${styles.text} ${styles.textItem}`}>
              <strong>Foodgram</strong> — это онлайн-платформа, созданная в рамках обучения в Яндекс Практикуме, позволяющая пользователям удобно сохранять, публиковать и делиться кулинарными рецептами.
            </p>

            <p className={`${styles.text} ${styles.textItem}`}>
              Основная идея проекта — упростить процесс планирования готовки и покупок. Сайт предоставляет возможность:
            </p>

            <ul className={styles.text}>
              <li className={styles.textItem}>создавать и редактировать собственные рецепты;</li>
              <li className={styles.textItem}>добавлять рецепты в избранное и список покупок;</li>
              <li className={styles.textItem}>скачивать список ингредиентов одним кликом;</li>
              <li className={styles.textItem}>подписываться на любимых авторов.</li>
            </ul>

            <p className={`${styles.text} ${styles.textItem}`}>
              Регистрация доступна любому пользователю. Подтверждение email не требуется, вы можете использовать любой адрес.
            </p>

            <p className={`${styles.text} ${styles.textItem}`}>
              Проект реализован с нуля и является частью итоговой работы.
            </p>

            <h3 className={styles.additionalTitle}>Ссылки</h3>
            <p className={styles.text}>
              Исходный код проекта:&nbsp;
              <a
                href="https://github.com/Guram-Gurych/foodgram"
                className={styles.textLink}
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub
              </a>
              <br />
              Автор:&nbsp;
              <a
                href="https://t.me/grch_grm"
                className={styles.textLink}
                target="_blank"
                rel="noopener noreferrer"
              >
                Бледных Кирилл
              </a>
            </p>
          </div>
        </div>
      </Container>
    </Main>
  )
}

export default About
