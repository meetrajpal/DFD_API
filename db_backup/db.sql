--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 16.8

-- Started on 2025-04-04 21:42:46

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 225 (class 1259 OID 16458)
-- Name: frame; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.frame (
    frame_id bigint NOT NULL,
    video_id bigint NOT NULL,
    user_id bigint NOT NULL,
    filename character varying NOT NULL,
    filepath character varying NOT NULL
);


ALTER TABLE public.frame OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16455)
-- Name: frame_frame_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.frame_frame_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.frame_frame_id_seq OWNER TO postgres;

--
-- TOC entry 4836 (class 0 OID 0)
-- Dependencies: 222
-- Name: frame_frame_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.frame_frame_id_seq OWNED BY public.frame.frame_id;


--
-- TOC entry 224 (class 1259 OID 16457)
-- Name: frame_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.frame_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.frame_user_id_seq OWNER TO postgres;

--
-- TOC entry 4837 (class 0 OID 0)
-- Dependencies: 224
-- Name: frame_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.frame_user_id_seq OWNED BY public.frame.user_id;


--
-- TOC entry 223 (class 1259 OID 16456)
-- Name: frame_video_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.frame_video_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.frame_video_id_seq OWNER TO postgres;

--
-- TOC entry 4838 (class 0 OID 0)
-- Dependencies: 223
-- Name: frame_video_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.frame_video_id_seq OWNED BY public.frame.video_id;


--
-- TOC entry 218 (class 1259 OID 16427)
-- Name: invalid token; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."invalid token" (
    token_id bigint NOT NULL,
    token character varying NOT NULL
);


ALTER TABLE public."invalid token" OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16426)
-- Name: invalid token_token_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."invalid token_token_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."invalid token_token_id_seq" OWNER TO postgres;

--
-- TOC entry 4839 (class 0 OID 0)
-- Dependencies: 217
-- Name: invalid token_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."invalid token_token_id_seq" OWNED BY public."invalid token".token_id;


--
-- TOC entry 227 (class 1259 OID 24645)
-- Name: prediction; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prediction (
    pred_id bigint NOT NULL,
    pred_label character varying(5) NOT NULL,
    video_id bigint NOT NULL,
    user_id bigint NOT NULL
);


ALTER TABLE public.prediction OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 24643)
-- Name: prediction_pred_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prediction_pred_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prediction_pred_id_seq OWNER TO postgres;

--
-- TOC entry 4840 (class 0 OID 0)
-- Dependencies: 226
-- Name: prediction_pred_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prediction_pred_id_seq OWNED BY public.prediction.pred_id;


--
-- TOC entry 229 (class 1259 OID 24675)
-- Name: prediction_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prediction_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prediction_user_id_seq OWNER TO postgres;

--
-- TOC entry 4841 (class 0 OID 0)
-- Dependencies: 229
-- Name: prediction_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prediction_user_id_seq OWNED BY public.prediction.user_id;


--
-- TOC entry 228 (class 1259 OID 24659)
-- Name: prediction_video_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prediction_video_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prediction_video_id_seq OWNER TO postgres;

--
-- TOC entry 4842 (class 0 OID 0)
-- Dependencies: 228
-- Name: prediction_video_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prediction_video_id_seq OWNED BY public.prediction.video_id;


--
-- TOC entry 216 (class 1259 OID 16399)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    user_id integer NOT NULL,
    username character varying NOT NULL,
    name character varying(10) NOT NULL,
    email character varying NOT NULL,
    password character varying NOT NULL,
    verified_email boolean DEFAULT false NOT NULL
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16398)
-- Name: user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_user_id_seq OWNER TO postgres;

--
-- TOC entry 4843 (class 0 OID 0)
-- Dependencies: 215
-- Name: user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_user_id_seq OWNED BY public."user".user_id;


--
-- TOC entry 221 (class 1259 OID 16437)
-- Name: video; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.video (
    video_id bigint NOT NULL,
    user_id bigint NOT NULL,
    filename character varying NOT NULL,
    filepath character varying NOT NULL,
    source character varying NOT NULL,
    url character varying
);


ALTER TABLE public.video OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16436)
-- Name: video_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.video_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.video_user_id_seq OWNER TO postgres;

--
-- TOC entry 4844 (class 0 OID 0)
-- Dependencies: 220
-- Name: video_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.video_user_id_seq OWNED BY public.video.user_id;


--
-- TOC entry 219 (class 1259 OID 16435)
-- Name: video_video_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.video_video_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.video_video_id_seq OWNER TO postgres;

--
-- TOC entry 4845 (class 0 OID 0)
-- Dependencies: 219
-- Name: video_video_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.video_video_id_seq OWNED BY public.video.video_id;


--
-- TOC entry 4663 (class 2604 OID 16461)
-- Name: frame frame_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.frame ALTER COLUMN frame_id SET DEFAULT nextval('public.frame_frame_id_seq'::regclass);


--
-- TOC entry 4664 (class 2604 OID 16462)
-- Name: frame video_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.frame ALTER COLUMN video_id SET DEFAULT nextval('public.frame_video_id_seq'::regclass);


--
-- TOC entry 4665 (class 2604 OID 16463)
-- Name: frame user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.frame ALTER COLUMN user_id SET DEFAULT nextval('public.frame_user_id_seq'::regclass);


--
-- TOC entry 4661 (class 2604 OID 16430)
-- Name: invalid token token_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."invalid token" ALTER COLUMN token_id SET DEFAULT nextval('public."invalid token_token_id_seq"'::regclass);


--
-- TOC entry 4666 (class 2604 OID 24648)
-- Name: prediction pred_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction ALTER COLUMN pred_id SET DEFAULT nextval('public.prediction_pred_id_seq'::regclass);


--
-- TOC entry 4667 (class 2604 OID 24660)
-- Name: prediction video_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction ALTER COLUMN video_id SET DEFAULT nextval('public.prediction_video_id_seq'::regclass);


--
-- TOC entry 4668 (class 2604 OID 24676)
-- Name: prediction user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction ALTER COLUMN user_id SET DEFAULT nextval('public.prediction_user_id_seq'::regclass);


--
-- TOC entry 4659 (class 2604 OID 16402)
-- Name: user user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN user_id SET DEFAULT nextval('public.user_user_id_seq'::regclass);


--
-- TOC entry 4662 (class 2604 OID 16440)
-- Name: video video_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.video ALTER COLUMN video_id SET DEFAULT nextval('public.video_video_id_seq'::regclass);


--
-- TOC entry 4678 (class 2606 OID 16467)
-- Name: frame frame_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.frame
    ADD CONSTRAINT frame_pkey PRIMARY KEY (frame_id);


--
-- TOC entry 4672 (class 2606 OID 16434)
-- Name: invalid token invalid token_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."invalid token"
    ADD CONSTRAINT "invalid token_pkey" PRIMARY KEY (token_id);


--
-- TOC entry 4682 (class 2606 OID 24651)
-- Name: prediction prediction_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT prediction_pkey PRIMARY KEY (pred_id);


--
-- TOC entry 4670 (class 2606 OID 16407)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);


--
-- TOC entry 4680 (class 2606 OID 16469)
-- Name: frame user_video_frame_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.frame
    ADD CONSTRAINT user_video_frame_unique UNIQUE (video_id, user_id, filename);


--
-- TOC entry 4674 (class 2606 OID 16445)
-- Name: video video_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.video
    ADD CONSTRAINT video_pkey PRIMARY KEY (video_id);


--
-- TOC entry 4676 (class 2606 OID 16454)
-- Name: video video_userid_filename_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.video
    ADD CONSTRAINT video_userid_filename_unique UNIQUE (user_id, filename);


--
-- TOC entry 4684 (class 2606 OID 16470)
-- Name: frame frame_fkey_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.frame
    ADD CONSTRAINT frame_fkey_user FOREIGN KEY (user_id) REFERENCES public."user"(user_id);


--
-- TOC entry 4685 (class 2606 OID 16475)
-- Name: frame frame_fkey_video_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.frame
    ADD CONSTRAINT frame_fkey_video_id FOREIGN KEY (video_id) REFERENCES public.video(video_id);


--
-- TOC entry 4686 (class 2606 OID 24701)
-- Name: prediction pred_fkey_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT pred_fkey_user FOREIGN KEY (user_id) REFERENCES public."user"(user_id) ON DELETE CASCADE;


--
-- TOC entry 4687 (class 2606 OID 24696)
-- Name: prediction pred_fkey_video; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction
    ADD CONSTRAINT pred_fkey_video FOREIGN KEY (video_id) REFERENCES public.video(video_id) ON DELETE CASCADE;


--
-- TOC entry 4683 (class 2606 OID 24691)
-- Name: video video_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.video
    ADD CONSTRAINT video_fkey FOREIGN KEY (user_id) REFERENCES public."user"(user_id) ON DELETE CASCADE;


-- Completed on 2025-04-04 21:42:46

--
-- PostgreSQL database dump complete
--

