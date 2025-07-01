
USE HawwarDB
GO
 IF NOT EXISTS(SELECT * FROM sys.schemas WHERE [name] = N'dbo')      
     EXEC (N'CREATE SCHEMA dbo')                                   
 GO                                                               

USE HawwarDB
GO
IF  EXISTS (select * from sys.objects so join sys.schemas sc on so.schema_id = sc.schema_id where so.name = N'VW_MembersFees' and sc.name=N'dbo' AND type in (N'V'))
 DROP VIEW [dbo].[VW_MembersFees]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[VW_MembersFees]
AS
SELECT     me.Mem_ID, me.Mem_Name, me.Mem_Code, me.Mem_Address, me.Mem_HomePhone, me.Mem_Mobile, me.Mem_WorkPhone, f.Fee_ID, f.Fee_Year, f.Fee_Amount, 
                      f.Fee_Date, f.Fee_RecieptNumber, f.Fee_Status, f.Fee_User_ID
FROM         dbo.Members AS me INNER JOIN
                      dbo.Fees AS f ON me.Mem_ID = f.Fee_Mem_ID
WHERE     (me.Mem_Status = 21) AND (f.Fee_Status = 1)

GO
GO
