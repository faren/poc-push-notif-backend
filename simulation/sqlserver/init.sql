-- ============================================================
-- Init Script: DBMobile Simulation
-- ============================================================

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'DBMobile')
BEGIN
    CREATE DATABASE [DBMobile]
END
GO

USE [DBMobile]
GO

-- ============================================================
-- RefJnsNotif (Reference: Jenis Notifikasi)
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'RefJnsNotif')
BEGIN
    CREATE TABLE [dbo].[RefJnsNotif] (
        [KdJnsNotif] [tinyint]     NOT NULL,
        [NmJnsNotif] [varchar](100) NOT NULL,
        CONSTRAINT [PK_RefJnsNotif] PRIMARY KEY CLUSTERED ([KdJnsNotif] ASC)
    )
END
GO

-- Truncate and re-seed reference data idempotently
DELETE FROM [dbo].[RefJnsNotif]
GO

INSERT INTO [dbo].[RefJnsNotif] ([KdJnsNotif], [NmJnsNotif]) VALUES
    (1,  'Tagihan Iuran'),
    (5,  'Rating Pelayanan'),
    (13, 'Info Kepesertaan'),
    (15, 'Antrean'),
    (16, 'Info Pelayanan'),
    (21, 'Pengaduan / Keluhan')
GO

-- ============================================================
-- Notifikasi (exact match production schema)
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Notifikasi')
BEGIN
    CREATE TABLE [dbo].[Notifikasi](
        [NotifID]    [int]           IDENTITY(1,1) NOT NULL,
        [Nokapst]    [varchar](13)   NULL,
        [KdJnsNotif] [tinyint]       NOT NULL,
        [Pesan]      [varchar](500)  NULL,
        [Status]     [tinyint]       NOT NULL,
        [FUser]      [int]           NULL,
        [FDate]      [datetime]      NULL,
        [SendDate]   [datetime]      NULL,
        [Judul]      [varchar](150)  NULL,
        [Response]   [varchar](1000) NULL,
        [Schedule]   [datetime]      NOT NULL,
        [Parameter]  [varchar](100)  NULL,
        [UserID]     [bigint]        NULL,
        CONSTRAINT [PK_Notifikasi] PRIMARY KEY CLUSTERED ([NotifID] ASC)
    )

    CREATE NONCLUSTERED INDEX [IX_JUDUL_Status_FDate]
        ON [dbo].[Notifikasi] ([Judul] ASC, [Status] ASC, [FDate] ASC)

    CREATE NONCLUSTERED INDEX [IX_Notifikasi_Job]
        ON [dbo].[Notifikasi] ([Status] ASC, [FDate] DESC, [Schedule] ASC, [UserID] ASC)
        INCLUDE ([Nokapst],[KdJnsNotif],[Pesan],[Judul],[SendDate],[Response])

    CREATE NONCLUSTERED INDEX [IX_NOTIFIKASI_KDJNSNOTIF]
        ON [dbo].[Notifikasi] ([KdJnsNotif] ASC)

    CREATE NONCLUSTERED INDEX [IX_Notifikasi_UserID_Status]
        ON [dbo].[Notifikasi] ([UserID] ASC, [Status] ASC)
        INCLUDE ([NotifID],[SendDate])

    CREATE NONCLUSTERED INDEX [IX_SEARCH_TAGIHAN]
        ON [dbo].[Notifikasi] ([Nokapst] ASC, [KdJnsNotif] ASC, [FDate] ASC, [UserID] ASC, [Status] ASC, [Schedule] ASC)
        INCLUDE ([NotifID],[Pesan],[Judul],[SendDate],[Parameter])

    ALTER TABLE [dbo].[Notifikasi]
        ADD CONSTRAINT [NOTIFIKASI_STATUS] DEFAULT ((0)) FOR [Status]

    ALTER TABLE [dbo].[Notifikasi]
        ADD CONSTRAINT [DF_Notifikasi_Schedule] DEFAULT (GETDATE()) FOR [Schedule]

    ALTER TABLE [dbo].[Notifikasi]
        WITH CHECK ADD CONSTRAINT [FK_Notifikasi_RefJnsNotif]
        FOREIGN KEY ([KdJnsNotif]) REFERENCES [dbo].[RefJnsNotif] ([KdJnsNotif])
END
GO

PRINT 'DBMobile init complete: RefJnsNotif + Notifikasi created.'
GO
